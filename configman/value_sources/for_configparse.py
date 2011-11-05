import sys
import ConfigParser

import exceptions
import configman.namespace as ns
import configman.converters as conv
import configman
<<<<<<< HEAD
from configman import config_exceptions
=======
>>>>>>> master


class NotEnoughInformationException(exceptions.ValueException):
    pass

file_name_extension = 'ini'

can_handle = (ConfigParser,
              ConfigParser.RawConfigParser,  # just the base class, subclasses
                                             # will be detected too
              basestring,
             )


class ValueSource(object):

    def __init__(self, source,
                 config_manager=None,
                 top_level_section_name='top_level'):
        self.delayed_parser_instantiation = False
        self.top_level_section_name = top_level_section_name
        if source is ConfigParser:
            try:
                app = config_manager.get_option_by_name('_application')
                source = "%s.%s" % (app.value.app_name, file_name_extension)
            except AttributeError:
                # we likely don't have the _application object set up yet.
                # we need to delay the instantiation of the ConfigParser
                # until later.
                if source is None:
                    raise NotEnoughInformationException("Can't setup an ini "
                                                        "file without knowing "
                                                        "the file name")
                self.delayed_parser_instantiation = True
                return
        if isinstance(source, basestring):
            self.configparser = self._create_parser(source)
        elif isinstance(source, ConfigParser.RawConfigParser):
            self.configparser = source
        else:
            raise exceptions.CantHandleTypeException("don't know how to handle"
                                                     " %s." % str(source))

    @staticmethod
    def _create_parser(source):
        parser = ConfigParser.ConfigParser()
        parser.optionxform = str
        parser.read(source)
        return parser

    def get_values(self, config_manager, ignore_mismatches):
        """Return a nested dictionary representing the values in the ini file.
        In the case of this ValueSource implementation, both parameters are
        dummies."""
        if self.delayed_parser_instantiation:
            try:
                app = config_manager.get_option_by_name('_application')
                source = "%s%s" % (app.value.app_name, file_name_extension)
                self.configparser = self._create_parser(source)
                self.delayed_parser_instantiation = False
            except AttributeError:
                # we don't have enough information to get the ini file
                # yet.  we'll ignore the error for now
                return {}
        options = {}
        for a_section in self.configparser.sections():
            if a_section == self.top_level_section_name:
                prefix = ''
            else:
                prefix = "%s." % a_section
            for an_option in self.configparser.options(a_section):
                name = '%s%s' % (prefix, an_option)
                options[name] = self.configparser.get(a_section, an_option)
        return options

    @staticmethod
    def write(option_iter, output_stream=sys.stdout):
        print >> output_stream, '[top_level]'
        for qkey, key, val in option_iter():
            if isinstance(val, ns.Namespace):
                print >> output_stream, '[%s]' % key
                print >> output_stream, '# %s\n' % val._doc
            else:
                print >> output_stream, '# name:', qkey
                print >> output_stream, '# doc:', val.doc
                print >> output_stream, '# converter:', \
                   conv.py_obj_to_str(val.from_string_converter)
                val_str = configman.ConfigurationManager.option_value_str(val)
                print >> output_stream, '%s=%s\n' % (key, val_str)
