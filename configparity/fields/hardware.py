from .common import IntField


class BytesField(IntField):
    def __init__(self, default=None, readonly=False):
        super().__init__()

        self._default = default
        self._readonly = readonly
        self._low = 0

    @property
    def default(self):
        return self._default

    @property
    def readonly(self):
        return self._readonly

    def __call__(self, value=None, current=None):
        suffixes = [
            ('TB', 4),
            ('GB', 3),
            ('MB', 2),
            ('KB', 1),
            ('B', 0)]

        if current and value != current and self._readonly:
            self.field_readonly_exception()

        if value:
            try:
                is_str = isinstance(value, str)

                is_num = any([
                    isinstance(value, int),
                    isinstance(value, float),
                    is_str and value.isdigit()])

                if is_num:
                    value = int(value)
                elif is_str:
                    for suffix in suffixes:
                        if suffix[0] in value:
                            value = int(value.split(suffix[0])[0]) * 1024 ** suffix[1]
                            break

            except Exception:
                self.field_value_exception(value)

        return value
