from configparity.models import Model
from configparity.fields.common import StrField
from configparity.fields.common import BoolField
from configparity.fields.common import IntField


class Enable(Model):
    password = StrField()
    encrypted = BoolField(default=False)
    level = IntField(low=0, high=15, default=0)
    pbkdf2 = BoolField(default=False)

    def __repr__(self):
        return f"Enable('{self.password}')"

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        config_str = config_str.split(' ')

        is_valid = all([
            config_str[0] == 'enable',
            config_str[1] == 'password',
            len(config_str) >= 3])

        if not is_valid:
            return None

        config = {
            'password': config_str[2],
            'encrypted': False,
            'level': 0,
            'pbkdf2': False}

        config_str = config_str[3:]

        while len(config_str) > 0:
            if config_str[0] == 'level' and len(config_str) > 1:
                config['level'] = config_str[1]
                config_str = config_str[2:]
                continue

            if config_str[0] == 'encrypted':
                config['encrypted'] = True

            if config_str[0] == 'pbkdf2':
                config['pbkdf2'] = True

            config_str = config_str[1:]

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([self.password])

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = f"enable password {self.password}"

        if self.encrypted:
            config += " encrypted"

        if self.level != 0:
            config += f" level {self.level}"

        if self.pbkdf2:
            config += " pbkdf2"

        return config

    @property
    def remove_config(self):
        if not self.is_valid:
            return None

        return f"no enable password {self.password}"
