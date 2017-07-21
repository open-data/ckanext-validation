# encoding: utf-8

import logging

import ckan.plugins as p
import ckantoolkit as t

from ckanext.validation import settings
from ckanext.validation.model import tables_exist
from ckanext.validation.logic import (
    resource_validation_run, resource_validation_show,
    auth_resource_validation_run, auth_resource_validation_show)


log = logging.getLogger(__name__)


class ValidationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        if not tables_exist():
            log.critical(u'''
The validation extension requires a database setup. Please run the following
to create the database tables:
    paster --plugin=ckanext-validation validation init-db
''')
        else:
            log.debug(u'Validation tables exist')

        t.add_template_directory(config_, u'templates')
        t.add_public_directory(config_, u'public')
        t.add_resource(u'fanstatic', u'validation')

    # IActions

    def get_actions(self):
        return {
            u'resource_validation_run': resource_validation_run,
            u'resource_validation_show': resource_validation_show
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            u'resource_validation_run': auth_resource_validation_run,
            u'resource_validation_show': auth_resource_validation_show
        }

    # IResourceController

    resources_to_validate = {}

    def after_create(self, context, resource):

        if not t.config.get(u'ckanext.validation.run_on_create', True):
            return

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
            _run_validation(resource['id'])

    def before_update(self, context, current_resource, updated_resource):

        if not t.config.get(u'ckanext.validation.run_on_update', True):
            return

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

    def after_update(self, context, updated_resource):

        if not t.config.get(u'ckanext.validation.run_on_update', True):
            return

        resource_id = updated_resource[u'id']

        if resource_id in self.resources_to_validate:
            del self.resources_to_validate[resource_id]

            _run_validation(resource_id)


def _run_validation(resource_id):

    try:
        t.get_action(u'resource_validation_run')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id})
    except t.ValidationError as e:
        log.warning(
            u'Could not run validation for resource {}: {}'.format(
                resource_id, str(e)))
