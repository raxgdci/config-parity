from configparity.models import Model
from configparity.fields.common import StrField
from configparity.fields.common import IntField
from configparity.fields.common import BoolField


class Vlan(Model):
    name = StrField()
    number = IntField(low=1, high=4094)
    shutdown = BoolField(default=False)

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        config_lines = [(l[1:] if l.startswith(' ') else l) for l in config_str.splitlines()]

        config = {}

        for line in config_lines:
            line = line.split(' ')
            field = line[0]
            value = True

            if field == 'vlan':
                field = 'number'

            if len(line) > 1:
                value = ' '.join(line[1:])

            config[field] = value

        is_valid = all([
            'name' in config,
            'number' in config])

        if not is_valid:
            return None

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.name,
            self.number])

    @property
    def config(self):
        if not self.is_valid:
            return None

        exclude = ['name', 'number']
        config = "vlan {}\n name {}".format(self.number, self.name)

        for key in self.values:
            value = self.values[key]

            if key not in exclude:
                if isinstance(value, bool):
                    config += "\n {}".format(key)
                else:
                    config += "\n {} {}".format(key, value)

        return config

    @property
    def rollback(self):
        if not self.config:
            return None

        return "no " + self.config.splitlines()[0]

    @property
    def disable(self):
        if not self.config:
            return None

        return self.config.splitlines()[0] + "\n shutdown"
