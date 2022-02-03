# encoding: utf-8

import logging
import datetime
import json
import re

import requests
from sqlalchemy.orm.exc import NoResultFound
from goodtables import validate
from goodtables.error import set_language

from ckan.model import Session
import ckan.lib.uploader as uploader

import ckantoolkit as t

from ckanext.validation.model import Validation


log = logging.getLogger(__name__)


def run_validation_job(resource):

    log.debug(u'Validating resource {}'.format(resource['id']))

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

    dataset = t.get_action('package_show')(
        {'ignore_auth': True}, {'id': resource['package_id']})

    source = None
    if resource.get('url_type') != 'upload':
        return  # only uploaded files may be validated for now

    url = resource.get('url')
    import urlparse
    url_parse = urlparse.urlsplit(url)
    filename = url_parse.path.split('/')[-1]
    from ckanext.cloudstorage.storage import ResourceCloudStorage
    storage = ResourceCloudStorage(resource)
    source = storage.get_url_from_filename(resource['id'], filename)

    schema = resource.get(u'schema')
    if schema and isinstance(schema, basestring):
        if schema.startswith('http'):
            r = requests.get(schema)
            schema = r.json()
        else:
            schema = json.loads(schema)

    _format = resource[u'format'].lower()

    reports = _validate_table(source, _format=_format, schema=schema, **options)

    for report in reports.values():
        # Hide uploaded files
        for table in report.get('tables', []):
            if table['source'].startswith('/'):
                table['source'] = resource['url']
        for index, warning in enumerate(report.get('warnings', [])):
            report['warnings'][index] = re.sub(r'Table ".*"', 'Table', warning)

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
         'validation_timestamp': validation.finished.isoformat()})


def _validate_table(source, _format=u'csv', schema=None, **options):

    reports = {}
    for lang in t.config.get(
            'ckanext.validation.locales_offered',
            t.config.get('ckan.locales_offered', 'en')).split():
        set_language(lang)
        reports[lang] = validate(source, format=_format, schema=schema, **options)

    log.debug(u'Validating source: {}'.format(source))

    return reports


def _get_site_user_api_key():

    site_user_name = t.get_action('get_site_user')({'ignore_auth': True}, {})
    site_user = t.get_action('get_site_user')(
        {'ignore_auth': True}, {'id': site_user_name})
    return site_user['apikey']
