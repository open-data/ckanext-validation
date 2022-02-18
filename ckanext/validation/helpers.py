# encoding: utf-8
import json

from ckan.lib.helpers import url_for_static
from ckantoolkit import url_for, _, config, asbool, literal, h
import ckan.plugins.toolkit as toolkit
from ckan.lib.helpers import render_datetime


def get_validation_badge(resource, in_listing=False):

    if in_listing and not asbool(
            config.get('ckanext.validation.show_badges_in_listings', True)):
        return ''

    try:
        validation = toolkit.get_action(u'resource_validation_show')(
            {u'ignore_auth': True},
            {u'resource_id': resource['id']})
    except toolkit.ObjectNotFound:
        return ''

    messages = {
        'success': _('Valid data'),
        'failure': _('Invalid data'),
        'error': _('Error during validation'),
        'unknown': _('Data validation unknown'),
    }

    if validation.get('status') in ['success', 'failure', 'error']:
        status = validation.get('status')
    else:
        status = 'unknown'

    validation_url = url_for(
        'validation_read',
        id=resource['package_id'],
        resource_id=resource['id'])

    timestamp = render_datetime(validation.get('finished'), with_hours=True) \
        if validation.get('finished') else ''

    return unicode('<a href="{validation_url}" class="validation-badge"><img '
                   'src="{badge_url}" alt="{alt}" title="{'
                   'title}"/></a>').format(
        validation_url=validation_url,
        badge_url=url_for_static('/images/badges/{lang}/data-{status}-flat.svg'
                                 .format(lang=h.lang(), status=status)),
        alt=messages[status],
        title=timestamp)


def validation_extract_report_from_errors(errors):

    report = None
    for error in errors.keys():
        if error == 'validation':
            report = errors[error][0]
            # Remove full path from table source
            source = report['tables'][0]['source']
            report['tables'][0]['source'] = source.split('/')[-1]
            msg = _('''
There are validation issues with this file, please see the
<a {params}>report</a> for details. Once you have resolved the issues,
click the button below to replace the file.''')
            params = [
                'href="#validation-report"',
                'data-module="modal-dialog"',
                'data-module-div="validation-report-dialog"',
            ]
            new_error = literal(msg.format(params=' '.join(params)))
            errors[error] = [new_error]
            break

    return report, errors


def dump_json_value(value, indent=None):
    """
    Returns the object passed serialized as a JSON string.

    :param value: The object to serialize.
    :returns: The serialized object, or the original value if it could not be
        serialized.
    :rtype: string
    """
    try:
        return json.dumps(value, indent=indent, sort_keys=True)
    except (TypeError, ValueError):
        return value


def bootstrap_version():
    if config.get('ckan.base_public_folder') == 'public':
        return '3'
    else:
        return '2'


def validation_status(resource_id):
    try:
        validation = toolkit.get_action(u'resource_validation_show')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id})
        return validation.get('status')
    except toolkit.ObjectNotFound:
        return 'unknown'
