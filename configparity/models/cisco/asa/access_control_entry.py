from configparity.models import Model
from configparity.fields.common import AllowedField
from configparity.fields.common import BoolField
from configparity.fields.common import IntField
from configparity.fields.common import StrField
from configparity.fields.networking import IPAddressField
from configparity.fields.networking import IPNetworkField
import ipaddress


class AccessControlEntry(Model):
    ALLOWED_PROTOCOLS = [
        "ah", "eigrp", "esp", "gre", "icmp", "icmp6", "igmp",
        "igrp", "ip", "ipinip", "ipsec", "nos", "ospf",
        "pcp", "pim", "pptp", "snp", "tcp", "udp", "url"]

    ALLOWED_TYPES = ['extended', 'remark', 'standard', 'webtype']
    ALLOWED_ACTIONS = ['deny', 'permit']

    PORT_OPERATORS = ['eq', 'gt', 'lt', 'neq', 'range']

    WEBTYPE_URL_PROTOCOLS = [
        "cifs", "citrix", "citrixs", "ftp", "http",
        "https", "imap4", "pop3", "smtp", "smart-tunnel",
        "nfs", "post", "vnc", "ssh", "telnet", "rdp"]

    name = StrField(readonly=True)
    input_line = StrField(readonly=True)
    type = StrField(allowed=ALLOWED_TYPES, readonly=True)
    action = StrField(allowed=ALLOWED_ACTIONS, readonly=True)
    protocol = AllowedField([
        IntField(low=0, high=255),
        StrField(allowed=ALLOWED_PROTOCOLS),
        IPAddressField(),
        IPNetworkField(),
        StrField()])
    remark = StrField()
    source = AllowedField([
        IPAddressField(),
        IPNetworkField(),
        StrField()])
    source_port = StrField()
    destination = AllowedField([
        IPAddressField(),
        IPNetworkField(),
        StrField()])
    destination_port = StrField()
    inactive = BoolField(default=False)
    log = BoolField(default=False)
    time_range = StrField()

    def __str__(self):
        return self.config

    def __repr__(self):
        return f"AccessControlEntry('{self.name}')"

    def parse_chunks(self, line):
        if isinstance(line, str):
            line = line.split(' ')

        chunk = ''
        chunks = []

        for word in line:
            just_one = any([
                'any' in word,
                len(chunks) == 0 and word.isdigit(),
                word in ['log', 'inactive'],
                word in self.ALLOWED_PROTOCOLS])

            if just_one:
                chunks.append(word)
                chunk = ''
                continue

            if chunk in ['', 'security-group', 'range']:
                if chunk != '':
                    chunk += ' '

                chunk += word

            else:
                chunks.append(f"{chunk} {word}")
                chunk = ''

        if chunk != '':
            chunks.append(chunk)

        return chunks

    @staticmethod
    def parse_standard_config(config, line):
        if line[0] == 'host':
            config['destination'] = line[1]
        else:
            config['destination'] = " ".join(line[0:])

        return config

    def parse_extended_config(self, config, line):
        chunks = self.parse_chunks(line)

        if chunks[0].split(' ')[0] == 'object' and len(chunks) == 1:
            config['protocol'] = " ".join(chunks[0:])
            return config

        keys = [
            'protocol',
            'source', 'source_port',
            'destination', 'destination_port',
            'bad_data_entered']

        port_value_keys_allowed = ['object-group'] + self.PORT_OPERATORS
        k = 0

        for chunk in chunks:
            chunk = chunk.split(' ')
            value_key = chunk[0]
            value = " ".join(chunk[1:]) if len(chunk) > 1 else None

            needs_more_context = all([
                config.get('protocol') in ['tcp', 'udp', '6', '17'],
                any([
                    len(chunks) in [3, 4] and 'object-group' in chunks[2],
                    len(chunks) == 4 and 'object-group' in chunks[3]])])

            if needs_more_context:
                return None

            if value_key in ['log', 'inactive', 'time-range']:
                if value_key == 'time-range':
                    config['time_range'] = value
                else:
                    config[value_key] = True

                continue

            skip_optional = all([
                'port' in keys[k],
                any([
                    len(chunks) <= 3,
                    config.get('protocol') and 'object-group' in config['protocol'],
                    value_key not in port_value_keys_allowed])])

            if skip_optional:
                k += 1

            if k > len(keys) - 1:
                k = len(keys) - 1

            key = keys[k]

            only_one = any([
                'any' in value_key,
                key == 'protocol' and value_key in self.ALLOWED_PROTOCOLS,
                key == 'protocol' and value_key.isdigit()])

            if value_key == 'host':
                config[key] = value

            elif only_one:
                config[key] = value_key

            else:
                config[key] = f"{value_key} {value}"

            k += 1

        return config

    def parse_webtype_config(self, config, line):
        chunks = self.parse_chunks(line)

        keys = ['protocol', 'destination', 'destination_port', 'bad_data_entered']
        k = 0

        for chunk in chunks:
            chunk = chunk.split(' ')
            value_key = chunk[0]
            value = " ".join(chunk[1:]) if len(chunk) > 1 else None

            if value_key in ['log', 'inactive', 'time-range']:
                if value_key == 'time-range':
                    config['time_range'] = value
                else:
                    config[value_key] = True

                continue

            if k > len(keys) - 1:
                k = len(keys) - 1

            key = keys[k]

            if value_key == 'host':
                config[key] = value

            elif 'any' in value_key or not value:
                config[key] = value_key

            else:
                config[key] = f"{value_key} {value}"

            k += 1

        return config

    def load_config(self, config_str):
        line = config_str.split(' ')

        is_valid = all([
            line[0] == 'access-list',
            line[1] not in ['alert-interval', 'deny-flow-max']])

        if not is_valid:
            return None

        config = {
            'name': line[1],
            'input_line': config_str}

        line = line[2:]
        new_config = None

        if line[0] in self.ALLOWED_TYPES:
            config['type'] = line[0]
            line = line[1:]

        if not config.get('type'):
            config['type'] = 'standard'

        if config['type'] == 'remark':
            config['remark'] = " ".join(line)

        elif config['type'] == 'standard':
            config['action'] = line[0]
            new_config = self.parse_standard_config(config, line[1:])

        elif config['type'] == 'extended':
            config['action'] = line[0]
            new_config = self.parse_extended_config(config, line[1:])

        elif config['type'] == 'webtype':
            config['action'] = line[0]
            new_config = self.parse_webtype_config(config, line[1:])

        config = new_config if new_config else config

        self.load_dict(**config)

    def load_dict(self, *args, **kwargs):
        super().load_dict(**kwargs)

        if not self.input_line:
            self.input_line = self.config

    @staticmethod
    def _validate(values=None):
        return all([
            values.get('name'),
            values.get('type'),
            any([
                values.get('action') and any([
                    values.get('source'),
                    values.get('destination')]),
                values.get('type') == 'remark' and values.get('remark')])])

    @property
    def is_valid(self):
        return self._validate(self.values)

    @staticmethod
    def generate_network_config(value):
        if isinstance(value, ipaddress.IPv4Network):
            return f"{value.network_address} {value.netmask}"

        return str(value)

    def generate_config(self, values=None):
        if not values:
            values = self.values

        config = f"access-list {values['name']} {values['type']}"

        if values['type'] == 'remark':
            config += f" {values.get('remark', '')}"

            return config

        config += f" {values['action']}"

        if values.get('protocol'):
            config += f" {values['protocol']}"

        if values.get('source'):
            config += f" {self.generate_network_config(values['source'])}"

            if values.get('source_port'):
                config += f" {values['source_port']}"

        if values.get('destination'):
            config += f" {self.generate_network_config(values['destination'])}"

            if values.get('destination_port'):
                config += f" {values['destination_port']}"

        if values.get('inactive'):
            config += " inactive"

        if values.get('log'):
            config += " log"

        if values.get('time_range'):
            config += f" time-range {values['time_range']}"

        return config

    @property
    def config(self):
        if not self.is_valid:
            return self.input_line if self.input_line and not self.onlyshowchanges else None

        return self.generate_config(self.values)

    @property
    def initial_config(self):
        if not self._validate(self.initial_values):
            input_line = self.initial_values.get('input_line')

            return input_line

        return self.generate_config(self.initial_values)
