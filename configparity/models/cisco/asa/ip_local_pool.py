from configparity.models import Model
from configparity.fields.common import StrField
from configparity.fields.networking import IPAddressField


class IPLocalPool(Model):
    name = StrField()
    start = IPAddressField()
    end = IPAddressField()
    mask = IPAddressField()

    def __repr__(self):
        return "IPLocalPool('{}')".format(self.name)

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        if 'ip local pool' not in config_str:
            return None

        config_str = config_str.split(' ')

        iprange = config_str[4].split('-')

        config = {
            'name': config_str[3],
            'start': iprange[0],
            'end': iprange[1],
            'mask': config_str[6]}

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.name,
            self.start,
            self.end,
            self.mask])

    @property
    def config(self):
        if not self.is_valid:
            return None

        return "ip local pool {} {}-{} mask {}".format(
            self.name,
            self.start,
            self.end,
            self.mask)
