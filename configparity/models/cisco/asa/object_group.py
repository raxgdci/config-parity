from configparity.models import Model
from configparity.models.cisco import COMMENTS
from configparity.fields.common import AllowedField
from configparity.fields.common import DictField
from configparity.fields.common import ListField
from configparity.fields.common import StrField
from configparity.fields.networking import IPAddressField
from configparity.fields.networking import IPNetworkField


class ObjectGroup(Model):
    ALLOWED_TYPES = [
        'icmp-type',
        'network',
        'protocol',
        'security',
        'service',
        'user']

    description = StrField()
    group_objects = ListField(default=[], list_type=StrField())
    icmp_objects = ListField(default=[], list_type=StrField())
    name = StrField()
    network_objects = ListField(default=[], list_type=AllowedField([
        IPAddressField(),
        IPNetworkField(),
        StrField()]))
    port_objects = ListField(default=[], list_type=StrField())
    protocol_groups = ListField(default=[], list_type=StrField())
    security_groups = ListField(default=[], list_type=StrField())
    service_objects = ListField(default=[], list_type=DictField())
    service_protocol = StrField()
    type = StrField(allowed=ALLOWED_TYPES)

    def __repr__(self):
        return "ObjectGroup('{}')".format(self.name)

    def __str__(self):
        return self.name

    def parse_network_object_config(self, line):
        if line[1] not in ['host', 'object']:
            if '.' in line[1] or ':' in line[1]:
                network = '/'.join(line[1:3])
                return network if network != '' else None

            return " ".join(line[1:])

        if line[1] == 'host':
            if '.' in line[2] or ':' in line[2]:
                return line[2]

            return 'host {}'.format(line[2])

        return " ".join(line[1:])

    def parse_service_object_config(self, line):
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

        for line in config_lines:
            line = line.split(' ')
            field = line[0]

            if field in COMMENTS:
                continue

            if field == 'object-group':
                config['type'] = line[1]
                config['name'] = line[2]

                if line[1] == 'service' and len(line) == 4:
                    config['service_protocol'] = line[3]

                continue

            if field == 'description':
                config[field] = ' '.join(line[1:])
                continue

            field = field.replace('-', '_') + 's'

            if field not in config:
                config[field] = []

            if field == 'network_objects':
                config[field].append(self.parse_network_object_config(line))
                continue

            if field == 'service_objects':
                config[field].append(self.parse_service_object_config(line))
                continue

            config[field].append(' '.join(line[1:]))

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.name,
            self.type in self.ALLOWED_TYPES])

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = "object-group {} {}".format(self.type, self.name)

        if self.service_protocol:
            config += " {}".format(self.service_protocol)

        string_lists = [
            'group_objects',
            'icmp_objects',
            'port_objects',
            'protocol_groups',
            'security_groups']

        for item_type in string_lists:
            for item in getattr(self, item_type):
                config += "\n {} {}".format(item_type.replace('_', '-')[:-1], item)

        for item in self.network_objects:
            if '/' in str(item) and '.' in str(item):
                item = "{} {}".format(item.network_address, item.netmask)

            elif ' ' not in str(item) and '.' in str(item) or ':' in str(item):
                item = "host {}".format(str(item))

            elif ' ' not in str(item):
                item = "object {}".format(str(item))

            config += "\n network-object {}".format(str(item))

        for item in self.service_objects:
            config += "\n service-object {}".format(item['protocol'])

            source = item['source']
            destination = item['destination']

            if source:
                config += " source {} {}".format(source[0], source[1])

            if destination:
                config += " destination {} {}".format(destination[0], destination[1])

        return config

    @property
    def remove_config(self):
        if not self.config:
            return None

        return "no " + self.config.splitlines()[0]
