from . import Field
from . import FieldValueException
from importlib import import_module
from datetime import datetime


class StrField(Field):
    def __init__(self, default=None, allowed=None, readonly=False):
        super().__init__()

        if allowed and not isinstance(allowed, list):
            allowed = [allowed]

        self._allowed = allowed
        self._default = default
        self._readonly = readonly

    @property
    def default(self):
        return self._default

    @property
    def readonly(self):
        return self._readonly

    def __call__(self, value=None, current=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                value = str(value)

                if self._allowed and value not in self._allowed:
                    self.field_value_exception(value)

            except Exception:
                self.field_value_exception(value)

        return value


class IntField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, value=None, current=None):
        try:
            value = int(value) if value else None

        except Exception:
            self.field_value_exception(value)

        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            if self._low and value < self._low or self._high and value > self._high:
                self.field_range_exception(value)

        self._changed = True

        return value


class FloatField(Field):
    def __init__(self, default=None, low=None, high=None, readonly=False):
        super().__init__()

        self._low = low
        self._high = high
        self._default = default
        self._readonly = readonly

    @property
    def default(self):
        return self._default

    @property
    def readonly(self):
        return self._readonly

    def __call__(self, value=None, current=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                value = float(value)

                if self._low and value < self._low or self._high and value > self._high:
                    self.field_range_exception(value)

            except Exception:
                self.field_value_exception(value)

        return value


class BoolField(Field):
    def __init__(self, default=None, readonly=False):
        super().__init__()

        self._default = default
        self._readonly = readonly

    @property
    def default(self):
        return self._default

    @property
    def readonly(self):
        return self._readonly

    def __call__(self, value=None, current=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                value = bool(value)

            except Exception:
                self.field_value_exception(value)

        return value


class ListField(Field):
    def __init__(self, list_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._list_type = list_type
        self.is_relational = True
        self.is_type_dynamic = self._list_type.is_type_dynamic

    def stringify_value(self, values):
        if not self.is_type_dynamic:
            return values

        return [self._list_type.stringify_value(value) for value in values]

    def __call__(self, value=None, current=None, from_model=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        values = value

        if values:
            try:
                new = []
                i = 0

                for item in value:
                    try:
                        current_item = None

                        if current and len(current) - 1 >= i:
                            current_item = current[i]

                        if self._list_type:
                            if 'is_relational' in dir(self._list_type) and self._list_type.is_relational:
                                from_model = self if not from_model else from_model

                                item = self._list_type(
                                    from_model=from_model,
                                    value=item,
                                    current=current_item)
                            else:
                                item = self._list_type(
                                    value=item,
                                    current=current_item)

                        new.append(item)
                        i += 1

                    except Exception:
                        self.field_value_exception(item)

                values = new

            except Exception:
                self.field_value_exception(values)

        return values


class TupleField(Field):
    def __init__(self, tuple_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._tuple_type = tuple_type
        self.is_relational = True
        self.is_type_dynamic = self._tuple_type.is_type_dynamic

    def stringify_value(self, values):
        if not self.is_type_dynamic:
            return values

        return tuple(self._tuple_type.stringify_value(value) for value in values)

    def __call__(self, value=None, current=None, from_model=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        values = value

        if values:
            try:
                new = []
                i = 0

                for item in value:
                    current_item = None

                    if current and len(current) - 1 >= i:
                        current_item = current[i]

                    if self._tuple_type:
                        if 'is_relational' in dir(self._tuple_type) and self._tuple_type.is_relational:
                            from_model = self if not from_model else from_model

                            item = self._tuple_type(
                                from_model=from_model,
                                value=item,
                                current=current_item)
                        else:
                            item = self._tuple_type(
                                value=item,
                                current=current_item)

                    new.append(item)
                    i += 1

                values = tuple(new)

            except Exception:
                self.field_value_exception(values)

        return values


class DictField(Field):
    def __init__(self, default=None, readonly=False, allowed=None):
        super().__init__()

        for pair in allowed or []:
            try:
                pair = tuple(pair)
            except Exception:
                self.field_allowed_type_exception(pair)

            if not pair[1] or not hasattr(pair[1], 'description'):
                self.field_allowed_type_exception(pair[1])

        self._default = default
        self._readonly = readonly
        self._allowed = allowed

    @property
    def default(self):
        return self._default

    @property
    def readonly(self):
        return self._readonly

    def _get_field_type(self, key):
        for pair in self._allowed or []:
            if pair[0] == key:
                return pair[1]

        return None

    def __call__(self, value=None, current=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                if current:
                    input_dict = dict(value)
                    value = current

                    allowed_keys = None

                    if self._allowed:
                        allowed_keys = [pair[0] for pair in self._allowed]

                    for key, new_value in input_dict.items():
                        if self._allowed and key not in allowed_keys:
                            self.field_key_exception(key)

                        field_type = self._get_field_type(key)

                        if field_type:
                            new_value = field_type(
                                value=new_value,
                                current=current)

                        value[key] = new_value
                else:
                    value = dict(value)

            except Exception:
                self.field_value_exception(value)

        return value


class DateTimeField(Field):
    def __init__(self, str_format, default=None, readonly=False):
        super().__init__()

        self._default = default
        self._format = str_format
        self._readonly = readonly

    @property
    def default(self):
        return self._default

    @property
    def format(self):
        return self._format

    @property
    def readonly(self):
        return self._readonly

    def __call__(self, value=None, current=None):
        if not self._format:
            self.field_invalid_format_exception()

        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                value = datetime.strptime(value, self._format)

            except Exception:
                self.field_datetime_exception(value, self._format)

        return value


class DateField(DateTimeField):
    def __call__(self, value=None, current=None):
        if not self._format:
            self.field_invalid_format_exception()

        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                value = datetime.strptime(value, self._format)
                value = value.date()

            except Exception:
                self.field_datetime_exception(value, self._format)

        return value


class TimeField(DateTimeField):
    def __call__(self, value=None, current=None):
        if not self._format:
            self.field_invalid_format_exception()

        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                value = datetime.strptime(value, self._format)
                value = value.time()

            except Exception:
                self.field_datetime_exception(value, self._format)

        return value


class EmailField(StrField):
    def __init__(self, readonly=False):
        super().__init__()

        self._readonly = readonly

    @property
    def readonly(self):
        return self._readonly

    def __call__(self, value=None, current=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            bad = False

            try:
                value = str(value)

            except Exception:
                bad = True

            bad = any([
                bad,
                ' ' in value,
                len(value.split('@') != 2 or '.' not in value.split('@')[1])])

            if bad:
                self.field_value_exception(value)

        return value


class AllowedField(Field):
    is_type_dynamic = True

    def __init__(self, field_types, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(field_types, tuple) and not isinstance(field_types, list):
            self.field_iterable_exception()

        if len(field_types) < 2:
            self.field_iterable_length_exception()

        for field_type in field_types:
            if not field_type or not hasattr(field_type, 'is_field'):
                self.field_allowed_type_exception(field_type)

        self.field_types = tuple(field_types)
        self.is_relational = True

    def should_force_str(self, value):
        for field_type in self.field_types:
            if not field_type.force_str_in_dict:
                continue

            try:
                if field_type == ModelField:
                    found = field_type(
                        from_model=self,
                        value=value,
                        current=value)
                else:
                    found = field_type(
                        value=value,
                        current=value)

                success = str(value)

            except FieldValueException:
                continue

            if found and success:
                return True

        return False

    def __call__(self, from_model=None, value=None, current=None):
        if not value:
            return None

        if current and value != current and self._readonly:
            self.field_readonly_exception()

        found = None
        good = False

        for field_type in self.field_types:
            try:
                if field_type == ModelField:
                    found = field_type(
                        from_model=from_model,
                        value=value,
                        current=current)
                else:
                    found = field_type(
                        value=value,
                        current=current)

                good = True
                break

            except FieldValueException:
                good = False

        if not good:
            self.field_value_exception(value)

        return found


class ModelField(Field):
    def _validate_model(self, model_input):
        try:
            model_path = 'configparity.models.' + '.'.join(model_input.split('.')[:-2])
            model_file = model_input.split('.')[-2]
            module = import_module('.' + model_file, package=model_path)
            model = getattr(module, model_input.split('.')[-1])

            return model

        except Exception:
            self.field_invalid_model_exception(model_input)

    def __init__(self, model, related_name=None, readonly=False):
        super().__init__()

        self.model = model
        self.related_name = related_name
        self.is_relational = True
        self._readonly = readonly

    @property
    def readonly(self):
        return self._readonly

    def __call__(self, from_model, value=None, current=None):
        if not value:
            return None

        if current and value != current and self._readonly:
            self.field_readonly_exception()

        model = self._validate_model(self.model)

        if isinstance(value, dict):
            value = model(**value)
        elif isinstance(value, str):
            value = model(from_config=value)

        if not isinstance(value, model):
            self.field_value_exception(value)

        if self.related_name:
            setattr(value, self.related_name, type(self))
            value.values[self.related_name] = from_model

        return value
