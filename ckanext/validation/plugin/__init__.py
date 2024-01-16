# encoding: utf-8
import os
import logging
import cgi
import json

import ckan.plugins as p
from ckan.lib.plugins import DefaultTranslation
import ckan.plugins.toolkit as toolkit

from ckanext.validation import settings
from ckanext.validation.model import tables_exist
from ckanext.validation.logic import (
    resource_validation_run, resource_validation_show,
    resource_validation_delete, resource_validation_run_batch,
    auth_resource_validation_run, auth_resource_validation_show,
    auth_resource_validation_delete, auth_resource_validation_run_batch,
    resource_create as custom_resource_create,
    resource_update as custom_resource_update,
)
from ckanext.validation.helpers import (
    get_validation_badge,
    validation_extract_report_from_errors,
    dump_json_value,
    bootstrap_version,
    validation_status,
)
from ckanext.validation.validators import (
    resource_schema_validator,
    validation_options_validator,
)
from ckanext.validation.utils import (
    get_create_mode_from_config,
    get_update_mode_from_config,
)
from ckanext.validation.interfaces import IDataValidation


log = logging.getLogger(__name__)


if toolkit.check_ckan_version(u'2.9'):
    from ckanext.validation.plugin.flask_plugin import MixinPlugin
    ckan_29_or_higher = True
else:
    from ckanext.validation.plugin.pylons_plugin import MixinPlugin
    ckan_29_or_higher = False


HERE = os.path.abspath(os.path.dirname(__file__))
I18N_DIR = os.path.join(HERE, u"../i18n")

class ValidationPlugin(MixinPlugin, p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IValidators)
    p.implements(p.ITranslation, inherit=True)

    # ITranslation

    def i18n_directory(self):
        return I18N_DIR

    # IConfigurer

    def update_config(self, config_):
#        if not tables_exist():
#            log.critical(u'''
#The validation extension requires a database setup. Please run the following
#to create the database tables:
#    paster --plugin=ckanext-validation validation init-db
#''')
#        else:
#            log.debug(u'Validation tables exist')

        toolkit.add_template_directory(config_, u'../templates')
        toolkit.add_public_directory(config_, u'../public')
        toolkit.add_resource(u'../fanstatic', 'ckanext-validation')

    # IActions

    def get_actions(self):
        new_actions = {
            u'resource_validation_run': resource_validation_run,
            u'resource_validation_show': resource_validation_show,
            u'resource_validation_delete': resource_validation_delete,
            u'resource_validation_run_batch': resource_validation_run_batch,
        }

        if get_create_mode_from_config() == u'sync':
            new_actions[u'resource_create'] = custom_resource_create
        if get_update_mode_from_config() == u'sync':
            new_actions[u'resource_update'] = custom_resource_update

        return new_actions

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            u'resource_validation_run': auth_resource_validation_run,
            u'resource_validation_show': auth_resource_validation_show,
            u'resource_validation_delete': auth_resource_validation_delete,
            u'resource_validation_run_batch': auth_resource_validation_run_batch,
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            u'get_validation_badge': get_validation_badge,
            u'validation_extract_report_from_errors': validation_extract_report_from_errors,
            u'dump_json_value': dump_json_value,
            u'bootstrap_version': bootstrap_version,
            u'validation_status': validation_status,
        }

    # IResourceController

    def _process_schema_fields(self, data_dict):
        u'''
        Normalize the different ways of providing the `schema` field

        1. If `schema_upload` is provided and it's a valid file, the contents
           are read into `schema`.
        2. If `schema_url` is provided and looks like a valid URL, it's copied
           to `schema`
        3. If `schema_json` is provided, it's copied to `schema`.

        All the 3 `schema_*` fields are removed from the data_dict.
        Note that the data_dict still needs to pass validation
        '''

        schema_upload = data_dict.pop(u'schema_upload', None)
        schema_url = data_dict.pop(u'schema_url', None)
        schema_json = data_dict.pop(u'schema_json', None)

        if isinstance(schema_upload, cgi.FieldStorage):
            data_dict[u'schema'] = schema_upload.file.read()
        elif schema_url:
            if (not isinstance(schema_url, basestring) or
                    not schema_url.lower()[:4] == u'http'):
                raise toolkit.ValidationError({u'schema_url': 'Must be a valid URL'})
            data_dict[u'schema'] = schema_url
        elif schema_json:
            data_dict[u'schema'] = schema_json

        return data_dict

    def before_create(self, context, data_dict):
        # (canada fork only): we add a context key,value here so we know that
        # in `after_create` that the `resource_create` action method happened.
        # There is no `before_create` for packages, only in `resource_create`.
        # TODO: remove after upstream fix to IResourceController hooks
        context['__resource_create'] = True
        return self._process_schema_fields(data_dict)

    resources_to_validate = {}

    def after_create(self, context, data_dict):

        is_dataset = self._data_dict_is_dataset(data_dict)

        if not get_create_mode_from_config() == u'async':
            return

        if is_dataset and not context.get('__resource_create'):
            for resource in data_dict.get(u'resources', []):
                self._handle_validation_for_resource(context, resource)
        else:
            # This is a resource.
            # (canada fork only): we want to run Validation on a single resource
            # if it is created via `resource_create`. We know this from the `before_create`
            # hook in this class. There is no `before_create` for packages.
            # TODO: revert after upstream fix to IResourceController hooks
            if '__resource_create' in context:
                del context['__resource_create']
            self._handle_validation_for_resource(context, data_dict)

    def _data_dict_is_dataset(self, data_dict):
        return (
            u'creator_user_id' in data_dict
            or u'owner_org' in data_dict
            or u'resources' in data_dict
            or data_dict.get(u'type') == u'dataset')

    def _handle_validation_for_resource(self, context, resource):
        needs_validation = False
        if ((
            # File uploaded
            resource.get(u'url_type') == u'upload' or
            # URL defined
            resource.get(u'url')
            ) and (
            # Make sure format is supported
            resource.get(u'format', u'').lower() in
                settings.SUPPORTED_FORMATS
                )):
            needs_validation = True

        if needs_validation:

            for plugin in p.PluginImplementations(IDataValidation):
                if not plugin.can_validate(context, resource):
                    log.debug('Skipping validation for resource {}'.format(resource['id']))
                    return

            _run_async_validation(resource[u'id'])

    def before_update(self, context, current_resource, updated_resource):
        # (canada fork only): add key,value to be used in `after_update`
        # to prevent all resources from re-validating after a single update.
        # There is no `before_update` for packages, only in `resource_update`.
        # TODO: remove after upstream fix to IResourceController hooks
        context['__resource_update'] = True

        updated_resource = self._process_schema_fields(updated_resource)

        if not get_update_mode_from_config() == u'async':
            return updated_resource

        needs_validation = False
        if ((
            # New file uploaded
            updated_resource.get(u'upload') or
            # External URL changed
            updated_resource.get(u'url') != current_resource.get(u'url') or
            # Schema changed
            (updated_resource.get(u'schema') !=
             current_resource.get(u'schema')) or
            # Format changed
            (updated_resource.get(u'format', u'').lower() !=
             current_resource.get(u'format', u'').lower())
            ) and (
            # Make sure format is supported
            updated_resource.get(u'format', u'').lower() in
                settings.SUPPORTED_FORMATS
                )):
            needs_validation = True

        if needs_validation:
            self.resources_to_validate[updated_resource[u'id']] = True

        return updated_resource

    def after_update(self, context, data_dict):

        is_dataset = self._data_dict_is_dataset(data_dict)

        # Need to allow create as well because resource_create calls
        # package_update
        if (not get_update_mode_from_config() == u'async'
                and not get_create_mode_from_config() == u'async'):
            return

        if context.get('_validation_performed'):
            # Ugly, but needed to avoid circular loops caused by the
            # validation job calling resource_patch (which calls
            # package_update)
            del context['_validation_performed']
            return

        # (canada fork only): check if `resource_create` or `resource_update` or `resource_delete`
        #  is happening. `__resource_create` will be delete in the `after_create` hook.
        # `__resource_delete` and `__resource_update` will be deleted here in `after_update` for resources.
        # TODO: remove after upstream fix to IResourceController hooks
        if is_dataset and not context.get('__resource_create') and \
        not context.get('__resource_delete') and not context.get('__resource_update'):
            for resource in data_dict.get(u'resources', []):
                if resource[u'id'] in self.resources_to_validate:
                    # This is part of a resource_update call, it will be
                    # handled on the next `after_update` call
                    continue
                else:
                    # This is an actual package_update call, validate the
                    # resources if necessary
                    #
                    # (canada fork only):
                    # NOTE: if a legit `package_update` or `package_patch` action happens,
                    # not via one of the resource actions, we cannot prevent the resubmission of
                    # all of the resources to Validation. `package_update` will not know which
                    # resources have actually changed or not.
                    #
                    # With that said, the blueprints (package edit and create form) use `allow_partial_update`
                    # context, so there will not actually be any resources when updating a package's metadata
                    # in the web browser. This is only an issue with the API calls to `/api/action/package_update`
                    # and `/api/action/package_patch`, and anywhere else in extensions that do not use the
                    # `allow_partial_update` context.
                    #
                    # TODO: this will be solved with the upstream fix to IResourceController hooks
                    self._handle_validation_for_resource(context, resource)

        else:
            # This is a resource
            resource_id = data_dict[u'id']

            # (canada fork only): delete the context key,value noting
            # that the `resource_delete` action is happening.
            # TODO: remove after upstream fix to IResourceController hooks
            context.pop('__resource_delete', None)
            context.pop('__resource_update', None)

            if resource_id in self.resources_to_validate:
                for plugin in p.PluginImplementations(IDataValidation):
                    if not plugin.can_validate(context, data_dict):
                        log.debug('Skipping validation for resource {}'.format(data_dict['id']))
                        return

                del self.resources_to_validate[resource_id]

                _run_async_validation(resource_id)

            if _should_remove_unsupported_resource_validation_reports(data_dict):
                p.toolkit.enqueue_job(fn=_remove_unsupported_resource_validation_reports, args=[resource_id],
                                      title="Remove Validation Reports for Unsupported Format or Type")

    def before_delete(self, context, resource, resources):
        # (canada fork only): add key,value to be used in `after_update`
        # to prevent all resources from re-validating after a single deletion.
        # TODO: remove after upstream fix to IResourceController hooks
        context['__resource_delete'] = True
        try:
            p.toolkit.get_action(u'resource_validation_delete')(
                context, {'resource_id': resource['id']})
            log.info('Validation report deleted for resource %s' % resource['id'])
        except toolkit.ObjectNotFound:
            log.error('Validation report for resource %s does not exist' % resource['id'])

    # IPackageController

    def before_index(self, index_dict):

        res_status = []
        dataset_dict = json.loads(index_dict['validated_data_dict'])
        for resource in dataset_dict.get('resources', []):
            if resource.get('validation_status'):
                res_status.append(resource['validation_status'])

        if res_status:
            index_dict['vocab_validation_status'] = res_status

        return index_dict

    # IValidators

    def get_validators(self):
        return {
            'resource_schema_validator': resource_schema_validator,
            'validation_options_validator': validation_options_validator,
        }


def _run_async_validation(resource_id):

    try:
        toolkit.get_action(u'resource_validation_run')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id,
             u'async': True})
    except toolkit.ValidationError as e:
        log.warning(
            u'Could not run validation for resource {}: {}'.format(
                resource_id, str(e)))


def _should_remove_unsupported_resource_validation_reports(res_dict):
    if not toolkit.h.asbool(toolkit.config.get('ckanext.validation.clean_validation_reports', False)):
        return False
    return ((not res_dict.get('format', u'').lower() in settings.SUPPORTED_FORMATS
                or res_dict.get('url_changed', False))
            and (res_dict.get('url_type') == 'upload'
                or res_dict.get('url_type') == '')
            and (res_dict.get('validation_status', False)
                or res_dict.get('extras', {}).get('validation_status', False)))


def _remove_unsupported_resource_validation_reports(resource_id):
    """
    Callback to remove unsupported validation reports.
    Controlled by config value: ckanext.validation.clean_validation_reports.
    Double check the resource format. Only supported Validation formats should have validation reports.
    If the resource format is not supported, we should delete the validation reports.
    """
    user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {"user": user['name']}

    try:
        res = toolkit.get_action('resource_show')(context, {"id": resource_id})
        pkg = toolkit.get_action('package_show')(context, {"id": res['package_id']})
    except toolkit.ObjectNotFound:
        log.error('Resource %s does not exist.' % res['id'])
        return

    # only remove validation reports from dataset types (canada fork only)
    if pkg['type'] != 'dataset':
        return

    if _should_remove_unsupported_resource_validation_reports(res):
        log.info('Unsupported resource format "{}". Deleting validation reports for resource {}'
            .format(res.get(u'format', u'').lower(), res['id']))
        try:
            toolkit.get_action('resource_validation_delete')(context, {"resource_id": res['id']})
            log.info('Validation reports deleted for resource %s' % res['id'])
        except toolkit.ObjectNotFound:
            log.error('Validation reports for resource %s do not exist' % res['id'])
