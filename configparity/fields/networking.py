import ipaddress
from .common import IntField
from .common import StrField


class IPAddressField(StrField):
    force_str_in_dict = True

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
                value = ipaddress.ip_address(value)

            except Exception:
                self.field_value_exception(value)

        return value


class IPNetworkField(StrField):
    force_str_in_dict = True

    def __init__(self, default=None, strict=True, readonly=False):
        super().__init__()

        self._default = default
        self._strict = strict
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
                value = str(value).replace(" ", "/")
                value = ipaddress.ip_network(value, strict=self._strict)

            except Exception:
                self.field_value_exception(value)

        return value


class MACAddressField(StrField):
    def __init__(self, default=None, splitter=None, split_at=None, readonly=False):
        super().__init__()

        self._default = default
        self._splitter = splitter or ':'
        self._split_at = split_at or 2
        self._readonly = readonly

    @property
    def default(self):
        return self._default

    @property
    def readonly(self):
        return self._readonly

    def _parse(self, value=None, current=None):
        if not value or len([c for c in value.lower() if c in "0123456789abcdef"]) != 12:
            self.field_value_exception(value)

        value = [c for c in value.lower() if c in "0123456789abcdef"]

        output = ""
        i = 0
        total = 0

        for char in value:
            output += char
            i = i + 1
            total += 1

            if (i == self._split_at) and total != len(value):
                output += self._splitter
                i = 0

        return output

    def __call__(self, value=None, current=None):
        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                value = self._parse(value)

            except Exception:
                self.field_value_exception(value)

        return value


class VLANField(IntField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._low = 1
        self._high = 4094
