from configparity.models import Model
from configparity.models.cisco import COMMENTS
from configparity.fields.common import BoolField
from configparity.fields.common import DictField
from configparity.fields.common import StrField
from configparity.fields.common import ModelField
from configparity.fields.common import TupleField
from configparity.fields.networking import IPAddressField
from configparity.fields.networking import IPNetworkField


class Object(Model):
    ALLOWED_TYPES = ['network', 'service']
    BOOL_FIELDS = [
        'call_home',
        'internal',
        'password_recovery',
        'resetoutside']

    call_home = BoolField(default=False)
    description = StrField()
    fqdn = StrField()
    host = IPAddressField()
    internal = BoolField(default=False)
    name = StrField()
    nat = ModelField('cisco.asa.nat.Nat', 'parent_object')
    password_recovery = BoolField(default=False)
    range = TupleField(tuple_type=IPAddressField())
    resetinbound_interface = StrField()
    resetoutbound_interface = StrField()
    resetoutside = BoolField(default=False)
    service = DictField()
    subnet = IPNetworkField()
    type = StrField(allowed=ALLOWED_TYPES)

    def __repr__(self):
        return "Object('{}')".format(self.name)

    def __str__(self):
        return self.name

    def parse_service_config(self, line):
        source = []
        destination = []

        for item in line[2:]:
            if item in ['destination', 'source']:
                item_type = item
            else:
                eval(item_type).append(item)

        return {
            'protocol': line[1],
            'source': tuple(source) if len(source) > 0 else None,
            'destination': tuple(destination) if len(destination) > 0 else None}

    def load_config(self, config_str):
        config_lines = [(l[1:] if l.startswith(' ') else l) for l in config_str.splitlines()]
        config = {}

        if config_lines[0].split(' ')[0] != 'object':
            return None

        for line in config_lines:
            line = line.split(' ')
            field = line[0].replace('-', '_')

            if field in COMMENTS:
                continue

            if field == 'object':
                config['type'] = line[1]
                config['name'] = line[2]
                continue

            if field == 'service':
                config[field] = self.parse_service_config(line)
                continue

            if isinstance(getattr(self, field), BoolField):
                config[field] = True
                continue

            if field in ['resetinbound', 'resetoutbound']:
                config["{}_interface".format(field)] = line[2]
                continue

            if field == 'nat':
                config[field] = " ".join(line)
                continue

            config[field] = " ".join(line[1:])

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.name,
            any([
                self.type and self.type == 'network' and any([
                    self.fqdn,
                    self.host,
                    self.nat,
                    self.range,
                    self.subnet]),
                self.type and self.type == 'service' and self.service and any([
                    self.service['destination'],
                    self.service['source']])])])

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = "object {} {}".format(self.type, self.name)

        if self.fqdn:
            config += "\n fqdn {}".format(self.fqdn)

        if self.host:
            config += "\n host {}".format(self.host)

        if self.nat:
            config += "\n " + self.nat.config

        if self.range:
            config += "\n range {} {}".format(self.range[0], self.range[1])

        if self.subnet:
            if ':' in str(self.subnet):
                network_str = str(self.subnet)
            else:
                network_str = "{} {}".format(self.subnet.network_address, self.subnet.netmask)

            config += "\n subnet {}".format(network_str)

        if self.type == 'service':
            config += "\n service "

        if self.service:
            config += self.service['protocol']

            if self.service['source']:
                config += " source {} {}".format(
                    self.service['source'][0],
                    self.service['source'][1])

            if self.service['destination']:
                config += " destination {} {}".format(
                    self.service['destination'][0],
                    self.service['destination'][1])

        if self.resetinbound_interface:
            config += "\n service resetinbound interface {}".format(self.resetinbound_interface)

        if self.resetoutbound_interface:
            config += "\n service resetoutbound interface {}".format(self.resetoutbound_interface)

        for setting in self.BOOL_FIELDS:
            if getattr(self, setting):
                config += "\n {}".format(setting.replace('_', '-'))

        return config

    @property
    def remove_config(self):
        if not self.config:
            return None

        return "no " + self.config.splitlines()[0]

    @property
    def remove_nat_config(self):
        if not self.config:
            return None

        line1 = self.config.splitlines()[0]

        return "{}\n no {}".format(line1, self.nat.config)
