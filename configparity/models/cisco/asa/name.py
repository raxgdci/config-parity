from configparity.models import Model
from configparity.fields.common import StrField
from configparity.fields.networking import IPAddressField


class Name(Model):
    name = StrField()
    ip_address = IPAddressField()

    def __repr__(self):
        return f"Name('{self.name}={self.ip_address}')"

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        config_str = config_str.split(' ')

        is_valid = all([
            config_str[0] == 'name',
            len(config_str) >= 3])

        if not is_valid:
            return None

        config = {
            'name': config_str[2],
            'ip_address': config_str[1]}

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.name,
            self.ip_address])

    @property
    def config(self):
        if not self.is_valid:
            return None

        return f"name {self.ip_address} {self.name}"

    @property
    def remove_config(self):
        if not self.config:
            return None

        return f"no {self.config}"
