from configparity.models import Model
from configparity.fields.common import StrField
from configparity.fields.common import BoolField
from configparity.fields.common import IntField


class Passwd(Model):
    password = StrField()
    encrypted = BoolField(default=False)

    def __repr__(self):
        return f"Passwd('{self.password}')"

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        config_str = config_str.split(' ')

        is_valid = all([
            config_str[0] == 'passwd',
            len(config_str) >= 2])

        if not is_valid:
            return None

        config = {
            'password': config_str[1],
            'encrypted': False}

        if len(config_str) == 3 and config_str[2] == 'encrypted':
            config['encrypted'] = True

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([self.password])

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = f"passwd {self.password}"

        if self.encrypted:
            config += " encrypted"

        return config

    @property
    def remove_config(self):
        if not self.is_valid:
            return None

        return f"no passwd {self.password}"
