# encoding: utf-8

import logging
import datetime
import json

import requests
from sqlalchemy.orm.exc import NoResultFound
from goodtables import validate
from goodtables.error import set_language

from ckan.model import Session

import ckantoolkit as t
from ckan.plugins.toolkit import config
from ckan.lib.uploader import get_resource_uploader

from ckanext.validation.model import Validation

try:
    from ckanext.canada.tabulate import CanadaCSVParser as CSVParser
except ImportError:
    from tabulator.parsers.csv import CSVParser


log = logging.getLogger(__name__)


def run_validation_job(resource):

    log.debug(u'Validating resource %s', resource['id'])

    try:
        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()
    except NoResultFound:
        validation = None

    if not validation:
        validation = Validation(resource_id=resource['id'])

    validation.status = u'running'
    Session.add(validation)
    Session.commit()

    options = t.config.get(
        u'ckanext.validation.default_validation_options')
    if options:
        options = json.loads(options)
    else:
        options = {}

    resource_options = resource.get(u'validation_options')
    if resource_options and isinstance(resource_options, basestring):
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

    # get url from uploader (canada fork only)
    #TODO: upstream contribution??
    upload = get_resource_uploader(resource)
    source = upload.get_path(resource['id'])
    log.info('Resource %s using uploader: %s', resource['id'], type(upload).__name__)

    schema = resource.get(u'schema')
    if schema and isinstance(schema, basestring):
        if schema.startswith('http'):
            r = requests.get(schema)
            schema = r.json()
        else:
            schema = json.loads(schema)

    _format = resource[u'format'].lower()

    # (canada fork only): add support for static validation options.
    #                     do NOT set options=static_options to prevent it
    #                     from being saved in the resource_patch.
    if static_options:
        reports = _validate_table(source, _format=_format, schema=schema, **static_options)
    else:
        reports = _validate_table(source, _format=_format, schema=schema, **options)

    for report in reports.values():
        # Hide uploaded files
        for table in report.get('tables', []):
            if table['source'].startswith('/'):
                table['source'] = resource['url']
        for index, warning in enumerate(report.get('warnings', [])):
            report['warnings'][index] = warning.replace('"' + source + '"', '')

    if report['table-count'] > 0:
        validation.status = u'success' if report[u'valid'] else u'failure'
        validation.reports = reports
    else:
        validation.status = u'error'
        validation.error = {
            'message': '\n'.join(report['warnings']) or u'No tables found'}
    validation.finished = datetime.datetime.utcnow()
    Session.add(validation)
    Session.commit()

    # Store result status in resource
    t.get_action('resource_patch')(
        {'ignore_auth': True,
         'user': t.get_action('get_site_user')({'ignore_auth': True})['name'],
         '_validation_performed': True},
        {'id': resource['id'],
         'validation_status': validation.status,
         'validation_options': options,
         'validation_timestamp': validation.finished.isoformat()})

    # load successfully validated resources to datastore using xloader
    if validation.status == u'success':
        if 'xloader' in config.get('ckan.plugins'):
            t.get_action('xloader_submit')(
                {'ignore_auth': True,
                 'user': t.get_action('get_site_user')({'ignore_auth': True})[
                     'name']},
                {'resource_id': resource['id']})


def _validate_table(source, _format=u'csv', schema=None, **options):

    http_session = options.pop('http_session', None) or requests.Session()
    use_proxy = 'ckan.download_proxy' in t.config
    if use_proxy:
        proxy = t.config.get('ckan.download_proxy')
        log.debug(u'Download resource for validation via proxy: %s', proxy)
        http_session.proxies.update({'http': proxy, 'https': proxy})

    reports = {}
    langs = t.config.get('ckanext.validation.locales_offered',
                         t.config.get('ckan.locales_offered', 'en'))
    if not langs:
        langs = t.config.get('ckan.locale_default', 'en')

    # (canada fork only): extra logging
    log.debug(u'Validating up to %s rows', options.get('row_limit', 1000))
    if options.get('skip_checks') and isinstance(options.get('skip_checks'), list):
        # log any skip checks in case they got into the request
        log.debug(u'Skipping checks: %r', options.get('skip_checks'))
    if options.get('checks'):
        # log the checks for debugging purposes
        log.debug(u'Using checks: %r', options.get('checks'))
    if options.get('encoding'):
        # log if using static encoding
        log.debug(u'Using Static Encoding for %s: %s', _format, options.get('encoding'))
    # (canada fork only): static dialect
    if options.get('dialect') and _format in options.get('dialect'):
        # subclassed Tabulator Stream will expect static_dialect
        options['static_dialect'] = options.get('dialect')[_format]
        # need to pass custom parser to use static dialect
        options['custom_parsers'] = {'csv': CSVParser}
        # pass log for subclass static dialect logging
        options['logger'] = log

    for lang in langs.split():
        set_language(lang)
        reports[lang] = validate(source, format=_format, schema=schema, http_session=http_session, **options)

    log.debug(u'Validating source: %s', source)

    return reports


def _get_site_user_api_key():

    site_user_name = t.get_action('get_site_user')({'ignore_auth': True}, {})
    site_user = t.get_action('get_site_user')(
        {'ignore_auth': True}, {'id': site_user_name})
    return site_user['apikey']
