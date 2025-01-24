# encoding: utf-8

# (canada fork only): ckan.plugins.toolkit
from ckan.plugins.toolkit import config

# TODO: configurable
DEFAULT_SUPPORTED_FORMATS = [u'csv', u'xls', u'xlsx', 'CSV', 'XLS', 'XLSX']  # (canada fork only): uppercase for schema choices


SUPPORTED_FORMATS = config.get(
    u'ckanext.validation.formats', DEFAULT_SUPPORTED_FORMATS)
