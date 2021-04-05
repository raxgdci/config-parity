from collections.abc import Iterable
from importlib import import_module
from pkgutil import iter_modules
from os import path
import copy
import json
import sys


class ModelConfigException(BaseException):
    pass


class Model(object):
    """
    This is the base model where common functions for a model can exist
    It also does the work to override values that have a predetermined field type
    Field Types are set at the top of a model importing this base Model class
    """

    is_model = True

    def __init__(self, from_config=None, **kwargs):
        self._fields = []
        self._key_types = {}

        self.values = {}
        self.readonly_keys = []
        self.only_changes_keys = []
        self.onlyshowchanges = False

        if from_config:
            self.load_config(from_config)
        else:
            self.load_dict(**kwargs)

    def __call__(self, from_config=None, **kwargs):
        if from_config:
            self.load_config(from_config)
        else:
            self.load_dict(**kwargs)

    def __setattr__(self, field, value):
        if field in dir(self) or hasattr(self, field):
            field_instance = object.__getattribute__(self, field)

            if 'is_field' in dir(field_instance):
                if 'is_relational' in dir(field_instance) and field_instance.is_relational:
                    self.values[field] = field_instance(
                        from_model=self,
                        value=value,
                        current=self.values.get(field))

                else:
                    self.values[field] = field_instance(
                        value=value,
                        current=self.values.get(field))

                return

        object.__setattr__(self, field, value)

    def __getattribute__(self, field):
        try:
            if field in object.__getattribute__(self, 'values'):
                return object.__getattribute__(self, 'values')[field]

        except AttributeError:
            # this error is occurring because __getattribute__ is being called before __init__
            object.__setattr__(self, 'values', {})

        field_instance = object.__getattribute__(self, field)

        if 'is_field' in dir(field_instance):
            value = field_instance.default if 'default' in dir(field_instance) else None
            object.__getattribute__(self, 'values')[field] = value
            return value

        return field_instance

    def __repr__(self):
        return "Model('')"

    def __str__(self):
        return ''

    @property
    def dictionary(self):
        dictionary = {}

        for field in self._fields or []:
            value = self.values.get(field)
            field_instance = object.__getattribute__(self, field)

            if 'is_field' not in dir(field_instance):
                continue

            if isinstance(value, list) or isinstance(value, tuple):
                items = []

                for item in value:
                    if isinstance(item, Model):
                        item = item.dictionary

                    items.append(item)

                value = tuple(items) if isinstance(value, tuple) else items

            elif isinstance(value, dict):
                items = {}

                for key, item in value.items():
                    if isinstance(item, Model):
                        item = item.dictionary

                    items[key] = item

                value = items

            elif isinstance(value, Model):
                value = value.dictionary

            value = field_instance.stringify_value(value)

            dictionary[field] = value

        return dictionary

    @property
    def json(self):
        return json.dumps(self.dictionary)

    def get_field_instance(self, field):
        if field in dir(self) or hasattr(self, field):
            return object.__getattribute__(self, field)

        return None

    def load_dict(self, **kwargs):
        for field, value in kwargs.items():
            field_instance = object.__getattribute__(self, field)

            if 'is_relational' in dir(field_instance) and field_instance.is_relational:
                self.values[field] = field_instance(
                    from_model=self,
                    value=value,
                    current=self.values.get(field))
            else:
                self.values[field] = field_instance(
                    value=value,
                    current=self.values.get(field))

            if field not in self._fields:
                self._fields.append(field)

            if field_instance.readonly and field not in self.readonly_keys:
                self.readonly_keys.append(field)

            if field_instance.hide_from_changes and field not in self.only_changes_keys:
                self.only_changes_keys.append(field)

        if 'initial_values' not in dir(self):
            object.__setattr__(self, 'initial_values', copy.deepcopy(self.values))

    def load_config(self, config):
        error = '"load_config" function has not be implemented for this model!'
        tb = sys.exc_info()[2]

        raise ModelConfigException(error).with_traceback(tb)

    @property
    def is_valid(self):
        error = '"is_valid" function has not be implemented for this model!'
        tb = sys.exc_info()[2]

        raise ModelConfigException(error).with_traceback(tb)

    @property
    def config(self):
        return None

    @property
    def rollback(self):
        return None

    @property
    def only_changes(self):
        changes = {}

        if 'initial_values' in dir(self) and 'values' in dir(self):
            for key in self.readonly_keys:
                initial = self.initial_values.get(key)

                if initial and key not in self.only_changes_keys:
                    changes[key] = initial

            for key, current in self.values.items():
                initial = self.initial_values.get(key)

                if isinstance(current, list):
                    current = [i for i in current if i not in initial]

                has_changes = any([
                    not isinstance(current, list) and initial != current,
                    isinstance(current, list) and len(current) > 0])

                if has_changes and key not in self.only_changes_keys:
                    changes[key] = current

            for key, initial in self.initial_values.items():
                current = self.values.get(key)

                if isinstance(current, list):
                    current = [i for i in current if i not in initial]

                has_changes = any([
                    not isinstance(current, list) and initial != current,
                    isinstance(current, list) and len(current) > 0])

                if has_changes and key not in self.only_changes_keys:
                    changes[key] = current

        if changes == {}:
            return None

        savevalues = self.values
        self.values = changes
        self.onlyshowchanges = True

        config = self.config

        self.values = savevalues
        self.onlyshowchanges = False

        return config


"""
This fancy code automatically imports modules from the files
in the models folder upon initialization.
"""
modules = []

for (_, name, _) in iter_modules([path.dirname(__file__)]):
    modules.append(name)
    imported_module = import_module('.' + name, package='configparity.models')
    class_name = list(filter(lambda x: not x.startswith('__'), dir(imported_module)))

del import_module
del iter_modules
del path
del imported_module
del class_name
