from importlib import import_module
from pkgutil import iter_modules
from os import path
import sys

"""
Fields are used with models to enforce type standards and automatically
convert fields to a specific value type. Fields can also house common
actions for each field type.
"""


class FieldValueException(BaseException):
    pass


class Field(object):
    is_field = True
    is_type_dynamic = False
    force_str_in_dict = False

    def __init__(self, *args, **kwargs):
        self.description = self.__class__.__name__
        self.no_exceptions = False

        self._low = kwargs.get('low')
        self._high = kwargs.get('high')
        self._default = kwargs.get('default')
        self._readonly = kwargs.get('readonly') or False
        self._hide_from_changes = kwargs.get('hide_from_changes') or True

    @property
    def default(self):
        return self._default

    @property
    def readonly(self):
        return self._readonly

    @property
    def hide_from_changes(self):
        return self._hide_from_changes

    def should_force_str(self, value):
        return self.force_str_in_dict

    def stringify_value(self, value):
        if self.should_force_str(value):
            return str(value)

        return value

    def field_value_exception(self, value):
        if self.no_exceptions:
            return None

        error = f'"{value}" does not appear to be a valid {self.description} input'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_key_exception(self, key):
        if self.no_exceptions:
            return None

        error = f'"{key}" does not appear to be a valid {self.description} key'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_readonly_exception(self):
        if self.no_exceptions:
            return None

        error = f'{self.description} input is a read-only field'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_invalid_format_exception(self):
        if self.no_exceptions:
            return None

        error = f'{self.description} field requires a format to be specified'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_datetime_exception(self, value, str_format):
        if self.no_exceptions:
            return None

        error = f'{self.description} field value "{value}" did not match the specified format "{str_format}"'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_range_exception(self, value):
        if self.no_exceptions:
            return None

        error = f'"{value}" is out of range for this {self.description} input'
        error += f' LOW: {self._low} ' if self._low else ''
        error += f' HIGH: {self._high} ' if self._high else ''

        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_iterable_exception(self):
        if self.no_exceptions:
            return None

        error = f'The specified field types for {self.description} are not in an iterable format'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_iterable_length_exception(self):
        if self.no_exceptions:
            return None

        error = f'"{self.description}" does not have enough iterable field types'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_allowed_type_exception(self, value):
        if self.no_exceptions:
            return None

        error = f'"{value}" is not a valid input for {self.description}'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])

    def field_invalid_model_exception(self, value):
        if self.no_exceptions:
            return None

        error = f'"{value}" is not a valid model type input for {self.description}'
        raise FieldValueException(error).with_traceback(sys.exc_info()[2])


"""
This fancy code automatically imports fields from the files
in the fields folder upon initialization.
"""
modules = []

for (_, name, _) in iter_modules([path.dirname(__file__)]):
    modules.append(name)
    imported_module = import_module('.' + name, package='configparity.fields')
    class_name = list(filter(lambda x: not x.startswith('__'), dir(imported_module)))

del import_module
del iter_modules
del path
del imported_module
del class_name
