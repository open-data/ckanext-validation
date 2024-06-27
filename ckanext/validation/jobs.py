# encoding: utf-8

import logging
import datetime
import json
import re

import requests
from sqlalchemy.orm.exc import NoResultFound
from frictionless import validate, system, Report, Schema, Dialect, Check, i18n

from ckan.model import Session

import ckantoolkit as t
from ckan.plugins import plugin_loaded
from ckan.lib.uploader import get_resource_uploader

from ckanext.validation.model import Validation
from ckanext.validation.utils import get_update_mode_from_config


log = logging.getLogger(__name__)


def run_validation_job(resource):

    log.debug('Validating resource %s', resource['id'])

    try:
        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()
    except NoResultFound:
        validation = None

    if not validation:
        validation = Validation(resource_id=resource['id'])

    validation.status = 'running'
    Session.add(validation)
    Session.commit()

    options = t.config.get(
        'ckanext.validation.default_validation_options')
    if options:
        options = json.loads(options)
    else:
        options = {}

    resource_options = resource.get('validation_options')
    if resource_options and isinstance(resource_options, str):
        resource_options = json.loads(resource_options)
    if resource_options:
        options.update(resource_options)

    # (canada fork only): add support for static validation options.
    #                     these should NOT be saved in the resource_patch.
    # TODO: upstream contribution??
    static_options = t.config.get(
        u'ckanext.validation.static_validation_options')
    if static_options:
        static_options = json.loads(static_options)

    source = None
    if resource.get('url_type') == 'upload':
        # (canada fork only): get url from uploader
        #TODO: upstream contribution??
        upload = get_resource_uploader(resource)
        source = upload.get_path(resource['id'])
        log.info('Resource %s using uploader: %s', resource['id'], type(upload).__name__)

    if not source:
        source = resource['url']

    schema = resource.get('schema')
    if schema:
        if isinstance(schema, str):
            if schema.startswith('http'):
                r = requests.get(schema)
                schema = r.json()
            schema = json.loads(schema)

    _format = resource['format'].lower()

    # (canada fork only): add support for static validation options.
    #                     do NOT set options=static_options to prevent it
    #                     from being saved in the resource_patch.
    if static_options:
        report = _validate_table(source, _format=_format, schema=schema, **static_options)
    else:
        report = _validate_table(source, _format=_format, schema=schema, **options)

    # Hide uploaded files
    if type(report) == Report:
        report = report.to_dict()

    if 'tasks' in report:
        for table in report['tasks']:
            if table['place'].startswith('/'):
                table['place'] = resource['url']
    if 'warnings' in report:
        validation.status = 'error'
        for index, warning in enumerate(report['warnings']):
            report['warnings'][index] = re.sub(r'Table ".*"', 'Table', warning)
    if 'valid' in report:
        validation.status = 'success' if report['valid'] else 'failure'
        #FIXME: report vs dict
        if isinstance(report, dict):
            validation.report = json.dumps(report)
        else:
            validation.report = json.dump(report.to_json())
    else:
        #FIXME: report vs dict
        if isinstance(report, dict):
            validation.report = json.dumps(report)
        else:
            validation.report = json.dump(report.to_json())
        if 'errors' in report and report['errors']:
            validation.status = 'error'
            validation.error = {
                'message': [str(err) for err in report['errors']]}
        else:
            validation.error = {'message': ['Errors validating the data']}
    validation.finished = datetime.datetime.utcnow()
    Session.add(validation)
    Session.commit()

    # Store result status in resource
    data_dict = {
        'id': resource['id'],
        'validation_status': validation.status,
        'validation_timestamp': validation.finished.isoformat(),
    }

    if get_update_mode_from_config() == 'sync':
        data_dict['_skip_next_validation'] = True,

    patch_context = {
        'ignore_auth': True,
        'user': t.get_action('get_site_user')({'ignore_auth': True})['name'],
        '_validation_performed': True
    }
    t.get_action('resource_patch')(patch_context, data_dict)

    # load successfully validated resources to datastore using xloader
    if validation.status == u'success':
        if plugin_loaded('xloader'):
            t.get_action('xloader_submit')(
                {'ignore_auth': True,
                 'user': t.get_action('get_site_user')({'ignore_auth': True})[
                     'name']},
                {'resource_id': resource['id']})




def _validate_table(source, _format='csv', schema=None, **options):

    # This option is needed to allow Frictionless Framework to validate absolute paths
    frictionless_context = { 'trusted': True }
    http_session = options.pop('http_session', None) or requests.Session()
    use_proxy = 'ckan.download_proxy' in t.config

    if use_proxy:
        proxy = t.config.get('ckan.download_proxy')
        log.debug('Download resource for validation via proxy: %s', proxy)
        http_session.proxies.update({'http': proxy, 'https': proxy})

    report = {}
    langs = t.config.get('ckanext.validation.locales_offered',
                         t.config.get('ckan.locales_offered', 'en'))
    if not langs:
        langs = t.config.get('ckan.locale_default', 'en')

    # (canada fork only): extra logging
    #FIXME: figure out max rows / min rows... table-dimensions check???
    log.debug(u'Validating up to %s rows', options.get('max_rows', 1000))
    if options.get('skip_checks') and isinstance(options.get('skip_checks'), list):
        log.debug(u'Skipping checks: %r', options.get('skip_checks'))
    if options.get('checks'):
        log.debug(u'Using checks: %r', options.get('checks'))
    if options.get('dialect') and _format in options.get('dialect'):
        log.debug(u'Using Static Dialect for %s: %r', _format, options.get('dialect')[_format])
    if options.get('encoding'):
        log.debug(u'Using Static Encoding for %s: %s', _format, options.get('encoding'))

    # (canada fork only): 2.10+ support
    # TODO: upstream contrib??
    if not isinstance(langs, list):
        langs = langs.split()

    frictionless_context['http_session'] = http_session
    resource_schema = Schema.from_descriptor(schema) if schema else None

    # Load the Resource Dialect as described in https://framework.frictionlessdata.io/docs/framework/dialect.html
    if 'dialect' in options:
        # (canada fork only): support static validation dialect options
        if _format in options.get('dialect'):
            dialect = Dialect.from_descriptor(options.get('dialect')[_format])
        else:
            dialect = Dialect.from_descriptor(options['dialect'])
        options['dialect'] = dialect

    # Load the list of checks and its parameters declaratively as in https://framework.frictionlessdata.io/docs/checks/table.html
    if 'checks' in options:
        checklist = [Check.from_descriptor(c) for c in options['checks']]
        options['checks'] = checklist

    with system.use_context(**frictionless_context):
        for lang in langs:
            # (canada fork only): i18n support
            i18n.set_language(lang)
            report[lang] = validate(source, format=_format, schema=resource_schema, **options)
        log.debug('Validating source: %s', source)

    return report


def _get_site_user_api_key():

    site_user_name = t.get_action('get_site_user')({'ignore_auth': True}, {})
    site_user = t.get_action('get_site_user')(
        {'ignore_auth': True}, {'id': site_user_name})
    return site_user['apikey']
