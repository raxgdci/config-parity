from configparity.models import Model
from configparity.fields.common import AllowedField
from configparity.fields.common import BoolField
from configparity.fields.common import IntField
from configparity.fields.common import StrField
from configparity.fields.networking import IPAddressField
from configparity.fields.networking import IPNetworkField


class Nat(Model):
    ALLOWED_TYPES = ['static', 'dynamic']

    after_auto = BoolField(default=False)
    description = StrField()
    destination = BoolField(default=False)
    destination_if_name = StrField()
    destination_mapped = AllowedField([IPAddressField(), IPNetworkField(), StrField()])
    destination_real = AllowedField([IPAddressField(), IPNetworkField(), StrField()])
    dns = BoolField(default=False)
    inactive = BoolField(default=False)
    interface = BoolField(default=False)
    ipv6 = BoolField(default=False)
    no_proxy_arp = BoolField(default=False)
    position = IntField(low=1, high=2147483647)
    route_lookup = BoolField(default=False)
    service = StrField()
    source = BoolField(default=False)
    source_if_name = StrField()
    source_mapped = AllowedField([IPAddressField(), IPNetworkField(), StrField()])
    source_real = AllowedField([IPAddressField(), IPNetworkField(), StrField()])
    type = StrField(allowed=ALLOWED_TYPES)
    unidirectional = BoolField(default=False)

    def __repr__(self):
        return "Translation('{}')".format(self.destination_mapped or self.destination_if_name)

    def __str__(self):
        if self.destination_mapped:
            return str(self.destination_mapped)
        elif self.destination_if_name:
            return str(self.destination_if_name)

        return ''

    def load_config(self, config_str):
        config_items = config_str.split(' ') if config_str[0] != ' ' else config_str[1:].split(' ')
        config = {}

        if config_items[0] != 'nat':
            return None

        config_items = config_items[1:]

        i = 0
        mode = None
        while i < len(config_items):
            add = 1
            item = config_items[i]

            if '(' in item:
                interfaces = item.replace('(', '').replace(')', '').split(',')
                config['source_if_name'] = interfaces[0]
                config['destination_if_name'] = interfaces[1]

            elif item in ['source', 'destination']:
                config[item] = True
                mode = item

            elif item in ['service', 'description']:
                config['service'] = config_items[i + 1]
                add = 2

            elif item in self.ALLOWED_TYPES:
                config['type'] = item

                if mode:
                    config["{}_real".format(mode)] = config_items[i + 1]
                    add = 2

                    if config_items[i + 2] not in dir(self) or not hasattr(self, config_items[i + 2]):
                        config["{}_mapped".format(mode)] = config_items[i + 2]
                        add = 3

                    mode = None
                else:
                    config["destination_mapped".format(mode)] = config_items[i + 1]
                    add = 2

            elif item.isdigit():
                config['position'] = item

            else:
                config[item.replace('-', '_')] = True

            i += add

        make_any = '::/0' if 'ipv6' in config else '0.0.0.0/0'

        for field in ['source_real', 'source_mapped', 'destination_real', 'destination_mapped']:
            if field in config:
                config[field] = config[field].replace('any', make_any)

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.source_if_name,
            self.destination_if_name,
            self.type,
            any([
                self.type == 'static' and self.destination_mapped,
                self.type == 'dynamic' and any([
                    self.source_real and self.source_mapped,
                    self.source_real and self.interface])])])

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = 'nat ({},{}) '.format(self.source_if_name, self.destination_if_name)

        if self.source:
            source_real = self.source_real
            source_mapped = self.source_mapped

            if '/' in str(source_real) and source_real.prefixlen == 0:
                source_real = 'any'

            if '/' in str(source_mapped) and source_mapped.prefixlen == 0:
                source_mapped = 'any'

            config += 'source {} {} {} '.format(self.type, source_real, source_mapped)

        if self.destination:
            destination_real = self.destination_real
            destination_mapped = self.destination_mapped

            if '/' in str(destination_real) and destination_real.prefixlen == 0:
                destination_real = 'any'

            if '/' in str(destination_mapped) and destination_mapped.prefixlen == 0:
                destination_mapped = 'any'

            config += 'destination {} {} {} '.format(self.type, destination_real, destination_mapped)

        if not self.source and not self.destination:
            destination_mapped = self.destination_mapped

            if '/' in str(destination_mapped) and destination_mapped.prefixlen == 0:
                destination_mapped = 'any'

            config += '{} {} '.format(self.type, destination_mapped)

        bool_types = [
            'after_auto',
            'dns',
            'inactive',
            'interface',
            'no_proxy_arp',
            'route_lookup',
            'unidirectional']

        for bool_type in bool_types:
            setting = getattr(self, bool_type)

            if setting:
                config += bool_type.replace('_', '-') + ' '

        return config[:-1]

    @property
    def remove_config(self):
        if not self.config:
            return None

        config = 'no ' + self.config

        if 'parent_object' in self.values:
            config = self.parent_object.config.splitlines()[0] + '\n' + config

        return config
