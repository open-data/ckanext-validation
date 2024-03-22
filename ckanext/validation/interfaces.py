from tabulator import Stream

from ckan.plugins.interfaces import Interface


class IDataValidation(Interface):

    def can_validate(self, context, data_dict):
        '''
        When implemented, this call can be used to control whether the
        data validation should take place or not on a specific resource.

        Implementations will receive a context object and the data_dict of
        the resource.

        If it returns False, the validation won't be performed, and if it
        returns True there will be a validation job started.

        Note that after this methods is called there are further checks
        performed to ensure the resource has one of the supported formats.
        This is controlled via the `ckanext.validation.formats` config option.

        Here is an example implementation:


        from ckan import plugins as p

        from ckanext.validation.interfaces import IDataValidation


        class MyPlugin(p.SingletonPlugin):

            p.implements(IDataValidation, inherit=True)

            def can_validate(self, context, data_dict):

                if data_dict.get('my_custom_field') == 'xx':
                    return False

                return True

        '''
        return True


# (canada fork only): interface for better Tabulator modifications
# TODO: upstream contrib??
class ITabulator(Interface):

    def get_dialect(self, format='csv'):
        """
        Return a dict with a valid file dialect.

        Use this if you want to specify dialects for a format.

        e.g. for csv:
        {
          "delimiter" : ",",
          "doublequote": True,
          "escapechar": None,
          "quotechar": "\"",
          "quoting": 0,
          "skipinitialspace": False,
          "lineterminator": "\r\n"
        }
        """
        return {}

    def get_stream_class(self):
        """
        Return a class of type Tabulator.Stream

        Use this if you want to subclass the Tabulator Stream class.
        """
        return Stream

    def get_parsers(self):
        """
        Return a dict of str,class for custom_parsers.

        Use this if you want to add new parsers, or override existing ones.

        e.g.
        {"csv": tabulator.parsers.csv.CSVParser}
        """
        return None

    def get_encoding(self):
        """
        Return a string to be used for specified encoding.

        Use this if you want to force encoding.

        e.g.
        utf-8
        """
        return None
