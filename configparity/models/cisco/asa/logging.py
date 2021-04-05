from configparity.models import Model
from configparity.fields.common import AllowedField
from configparity.fields.common import BoolField
from configparity.fields.common import DictField
from configparity.fields.common import EmailField
from configparity.fields.common import IntField
from configparity.fields.common import ListField
from configparity.fields.common import StrField
from configparity.fields.networking import IPAddressField


LEVEL_TYPES = [
    'asdm',
    'buffered',
    'console',
    'history',
    'mail',
    'monitor',
    'trap']

LEVELS = {
    0: 'emergencies',
    1: 'alerts',
    2: 'critical',
    3: 'errors',
    4: 'warnings',
    5: 'notifications',
    6: 'informational',
    7: 'debugging'}

CLASSES = [
    'auth', 'bridge', 'ca', 'citrix', 'config', 'csd', 'cts',
    'dap', 'eap', 'eapoudp', 'eigrp', 'email', 'ha', 'ids',
    'ip', 'ipaa', 'nac', 'nacpolicy', 'nacsettings', 'np',
    'ospf', 'rip', 'rm', 'rule-engine', 'session', 'snmp',
    'ssl', 'svc', 'sys', 'vm', 'vpdn', 'vpn', 'vpnc', 'vpnfo',
    'vpnlb', 'webfo', 'webvpn']


class Logging(Model):
    asdm = AllowedField([
        StrField(allowed=[v for k, v in LEVELS.items()]),
        StrField()])
    asdm_buffer_size = IntField(low=100, high=512)
    buffer_size = IntField(low=4096, high=1048576)
    buffered = AllowedField([
        StrField(allowed=[v for k, v in LEVELS.items()]),
        StrField()])

    # Holy crap, the level of inception here...
    # This creates the validators for the individual
    #  levels within the multilayer dict "classes"
    # Tuples within tuples within tuples,
    #  using list comprension to make the keys!
    classes = DictField(allowed=[(
        logging_class,
        DictField(allowed=[(
            level_type,
            StrField(allowed=[v for k, v in LEVELS.items()])
        ) for level_type in LEVEL_TYPES])
    ) for logging_class in CLASSES])

    console = AllowedField([
        StrField(allowed=[v for k, v in LEVELS.items()]),
        StrField()])
    debug_trace = BoolField(default=False)
    device_id = StrField()
    emblem = BoolField(default=False)
    enable = BoolField(default=False)
    facility = IntField(low=16, high=23, default=20)
    flash_bufferwrap = BoolField(default=False)
    flash_maximum_allocation = IntField(low=4, high=249592)
    flash_minimum_free = IntField(low=0, high=249592)
    flow_export_syslogs = StrField(allowed=['enable', 'disable'])
    from_address = StrField()
    ftp_bufferwrap = BoolField(default=False)
    ftp_server_address = AllowedField([IPAddressField(), StrField()])
    ftp_server_directory_path = StrField()
    ftp_server_username = StrField()
    ftp_server_password = StrField()
    ftp_server_password_encrypted = BoolField(default=False)
    hide_username = BoolField(default=True)
    history = AllowedField([
        StrField(allowed=[v for k, v in LEVELS.items()]),
        StrField()])

    # This craziness is also adding validation to a list of dicts
    hosts = ListField(
        list_type=DictField(
            allowed=[
                ('interface', StrField()),
                ('address', AllowedField([
                    IPAddressField(),
                    StrField()])),
                ('protocol', AllowedField([
                    IntField(low=6, high=6),  # TCP
                    IntField(low=17, high=17)])),  # UDP
                ('port', IntField(low=1, high=65535)),
                ('secure', BoolField(default=False)),
                ('format', StrField(allowed=['emblem']))]))

    # Some more of the same craziness that hosts is doing, but for lists!
    lists = ListField(
        list_type=DictField(
            allowed=[
                ('name', StrField()),
                ('level', StrField(allowed=[v for k, v in LEVELS.items()])),
                ('message', IntField(low=100000, high=999999)),
                ('class', StrField(c for c in CLASSES))]))

    mail = AllowedField([
        StrField(allowed=[v for k, v in LEVELS.items()]),
        StrField()])

    # Screw you, Cisco, for this level of complexity!
    # On a similar note, thank you, Cisco, for this level of customization!
    # Just more validation to a list of dicts
    messages = ListField(
        list_type=DictField(
            allowed=[
                ('level', StrField(allowed=[v for k, v in LEVELS.items()])),
                ('message', IntField(low=100000, high=999999)),
                ('no', BoolField(default=False))]))

    monitor = AllowedField([
        StrField(allowed=[v for k, v in LEVELS.items()]),
        StrField()])
    permit_hostdown = BoolField(default=False)
    queue = IntField(low=0, high=8192, default=512)

    # Understanding this logging stuff is love/hate
    # Yet more validation to a list of dicts
    rate_limits = ListField(
        list_type=DictField(
            allowed=[
                ('number', IntField(low=1, high=2147483647)),
                ('unlimited', BoolField(default=False)),
                ('interval', IntField(low=1, high=2147483647)),
                ('message', IntField(low=100000, high=999999)),
                ('level', IntField(low=0, high=7))]))

    # Because you can have multiple loggin levels sent to multiple email addresses,
    #  you need to be able to store multiple recipient-addresses. Which means
    #  this code you see has to validate this stuff, so here you go, more
    #  validator barf...
    recipient_addresses = ListField(
        list_type=DictField(
            allowed=[
                ('level', StrField(allowed=[v for k, v in LEVELS.items()])),
                ('email', EmailField())]))

    standby = BoolField(default=False)
    timestamp = BoolField(default=False)
    trap = AllowedField([
        StrField(allowed=[v for k, v in LEVELS.items()]),
        StrField()])

    def __repr__(self):
        enabled = 'Enabled' if self.enable else 'Not Enabled'
        return "Logging('{}')".format(enabled)

    def __str__(self):
        return self.config

    def parse_level_config(self, field, params, config):
        level = params[0]

        if level.isdigit():
            level = LEVELS.get(int(level)) or level

        config[field] = level

        return config

    def parse_class_config(self, params, config):
        class_type = params[0]
        level_type = params[1]
        level = LEVELS.get(int(params[2])) if params[2].isdigit() else params[2]

        if 'classes' not in config:
            config['classes'] = {}

        if class_type not in config['classes']:
            config['classes'][class_type] = {}

        config['classes'][class_type][level_type] = level

        return config

    def parse_list_config(self, params, config):
        list_item = {
            'name': params[0],
            'class': None,
            'level': None,
            'message': None}

        params = params[1:]
        changes = False

        while len(params) > 0:
            field = params[0]
            value = params[1]

            if field == 'level' and value.isdigit():
                value = LEVELS.get(int(value)) or value

            list_item[field] = value
            changes = True
            params = params[2:]

        if changes:
            if 'lists' not in config:
                config['lists'] = []

            config['lists'].append(list_item)

        return config

    def parse_ftp_server_config(self, params, config):
        config['ftp_server_address'] = params[0]
        config['ftp_server_directory_path'] = params[1]
        config['ftp_server_username'] = params[2]

        password = params[3]

        if params[3] in ['0', '8']:
            if params[3] == '8':
                config['ftp_server_password_encrypted'] = True
            else:
                config['ftp_server_password_encrypted'] = False

            password = params[4]

        if password != '*****':
            config['ftp_server_password'] = password

        return config

    def parse_host_config(self, params, config):
        host = {
            'interface': params[0],
            'address': params[1],
            'protocol': None,
            'port': None,
            'format': 'emblem' if 'emblem' in params else None,
            'secure': 'secure' in params}

        params = [p for p in params[2:] if p not in ['format', 'emblem', 'secure']]

        if len(params) > 0:
            protocol_and_port = params[0].split('/')
            protocol = protocol_and_port[0].lower()
            protocol = int(protocol) if protocol.isdigit() else protocol
            port = None

            if protocol in ['tcp', 'udp', 6, 17]:
                if protocol in ['tcp', 6]:
                    protocol = 6
                    port = 1470
                elif protocol in ['udp', 17]:
                    protocol = 17
                    port = 514

            if len(protocol_and_port) > 1 and protocol_and_port[1].isdigit():
                port = int(protocol_and_port[1])

            host['protocol'] = protocol
            host['port'] = port

        if 'hosts' not in config:
            config['hosts'] = []

        config['hosts'].append(host)

        return config

    def parse_message_config(self, params, enabled, config):
        message = {
            'no': not enabled,
            'level': None,
            'message': params[0]}

        if 'level' in params:
            level = params[-1]

            if level.isdigit():
                level = LEVELS.get(int(level)) or level

            message['level'] = level

        if 'messages' not in config:
            config['messages'] = []

        config['messages'].append(message)

        return config

    def parse_rate_limit_config(self, params, config):
        rate_limit = {
            'number': None,
            'unlimited': False,
            'interval': None,
            'message': None,
            'level': None}

        if params[0] == 'unlimited':
            rate_limit['unlimited'] = True
            params = params[1:]
        else:
            rate_limit['number'] = params[0]
            rate_limit['interval'] = params[1]
            params = params[2:]

        if params[0] == 'level':
            level = LEVELS.get(int(params[1])) if params[1].isdigit() else params[1]
            rate_limit['level'] = level
        elif params[0] == 'message':
            rate_limit['message'] = params[1]

        if 'rate_limits' not in config:
            config['rate_limits'] = []

        config['rate_limits'].append(rate_limit)

        return config

    def parse_recipient_address_config(self, params, config):
        level = LEVELS.get(int(params[2])) if params[2].isdigit() else params[2]

        recipient_address = {
            'email': params[0],
            'level': level}

        if 'recipient_addresses' not in config:
            config['recipient_addresses'] = []

        config['recipient_addresses'].append(recipient_address)

        return config

    def load_config(self, config_str):
        config_lines = [l for l in config_str.splitlines() if l.startswith('logging')]
        config = {}

        if len(config_lines) == 0:
            return None

        level_parsing = [
            'asdm', 'buffered', 'console', 'history',
            'mail', 'monitor', 'trap']

        for line in config_lines:
            line = line.split(' ')
            field = line[1].replace('-', '_')
            params = line[2:]
            enabled = True

            if line[0] == 'no':
                if line[1] != 'logging':
                    continue

                enabled = False
                field = line[2].replace('-', '_')
                params = line[3:]

            if field == 'hide':
                field += '_' + params[0]
                params = params[1:]

            if field in level_parsing:
                config = self.parse_level_config(field, params, config)
            elif field == 'class':
                config = self.parse_class_config(params, config)
            elif field == 'ftp_server':
                config = self.parse_ftp_server_config(params, config)
            elif field == 'host':
                config = self.parse_host_config(params, config)
            elif field == 'list':
                config = self.parse_list_config(params, config)
            elif field == 'message':
                config = self.parse_message_config(params, enabled, config)
            elif field == 'rate_limit':
                config = self.parse_rate_limit_config(params, config)
            elif field == 'recipient_address':
                config = self.parse_recipient_address_config(params, config)
            elif len(params) == 0:
                config[field] = enabled
            else:
                config[field] = " ".join(params)

        if config == {}:
            return None

        self.load_dict(**config)

    @property
    def is_valid(self):
        return True

    def generate_level_config(self, field):
        value = getattr(self, field)

        if not value:
            return ""

        return "logging {} {}".format(field, value)

    def generate_classes_config(self):
        if not self.classes or self.classes == {}:
            return ""

        lines = ""

        if self.onlyshowchanges:
            for class_type in self.initial_values['classes']:
                for level_type in self.initial_values['classes'][class_type]:
                    level = self.initial_values['classes'][class_type][level_type]

                    no = any([
                        class_type not in self.classes,
                        level_type not in self.classes[class_type]])

                    if no:
                        if lines != "":
                            lines += "\n"

                        lines += "no logging class {} {} {}".format(
                            class_type,
                            level_type,
                            level)

        for class_type in self.classes:
            for level_type in self.classes[class_type]:
                level = self.classes[class_type][level_type]

                if lines != "":
                    lines += "\n"

                lines += "logging class {} {} {}".format(
                    class_type,
                    level_type,
                    level)

        return lines

    def generate_ftp_server_config(self):
        if not self.ftp_server_address:
            if self.onlyshowchanges and self.initial_values['ftp_server_address']:
                password = self.initial_values['ftp_server_password'] or ""

                if password != "" and self.initial_values['ftp_server_password_encrypted']:
                    password = "8 " + password

                return "no logging ftp-server {} {} {} {}".format(
                    self.initial_values['ftp_server_address'],
                    self.initial_values['ftp_server_directory_path'],
                    self.initial_values['ftp_server_username'],
                    password)

            return ""

        password = self.ftp_server_password or ""

        if password != "" and self.ftp_server_password_encrypted:
            password = "8 " + password

        return "logging ftp-server {} {} {} {}".format(
            self.ftp_server_address,
            self.ftp_server_directory_path,
            self.ftp_server_username,
            password)

    def generate_hosts_config(self):
        if not self.hosts or len(self.hosts) == 0:
            return ""

        lines = ""

        for host in self.initial_values['hosts']:
            if host in self.hosts or not all([host['interface'], host['address']]):
                continue

            lines = lines + "\n" if lines != "" else lines
            lines += "no logging host {} {}".format(host['interface'], host['address'])

            if host['protocol']:
                protocol = str(host['protocol'])

                if host['port']:
                    protocol += "/{}".format(host['port'])

                lines += " {}".format(protocol)

            if host['secure'] and host['protocol'] == 6:
                lines += " secure"

            if host['format'] and host['protocol'] == 17:
                lines += " format {}".format(host['format'])

        for host in self.hosts:
            if not all([host['interface'], host['address']]):
                continue

            lines = lines + "\n" if lines != "" else lines
            lines += "logging host {} {}".format(host['interface'], host['address'])

            if host['protocol']:
                protocol = str(host['protocol'])

                if host['port']:
                    protocol += "/{}".format(host['port'])

                lines += " {}".format(protocol)

            if host['secure'] and host['protocol'] == 6:
                lines += " secure"

            if host['format'] and host['protocol'] == 17:
                lines += " format {}".format(host['format'])

        return lines

    def generate_lists_config(self):
        if not self.lists or len(self.lists) == 0:
            return ""

        lines = ""

        for item in self.lists:
            if not item['name']:
                continue

            line = "\n" if lines != "" else ""
            line += "logging list {}".format(item['name'])

            if item['message']:
                line += " message {}".format(item['message'])
                lines += line
                continue

            if not item['level']:
                continue

            line += " level {}".format(item['level'])

            if item['class']:
                line += " class {}".format(item['class'])

            lines += line

        return lines

    def generate_messages_config(self):
        if not self.messages or len(self.messages) == 0:
            return ""

        lines = ""

        for message in self.messages:
            if not message['message']:
                continue

            line = "\n" if lines != "" else ""
            line += "logging message {}".format(message['message'])

            if message['level']:
                line += " level {}".format(message['level'])
                lines += line
                continue

            if message['no']:
                line = "no {}".format(line)

            if not message['no'] and not self.onlyshowchanges:
                continue

            lines += line

        return lines

    def generate_rate_limits_config(self):
        if not self.rate_limits or len(self.rate_limits) == 0:
            return ""

        lines = ""

        for rate_limit in self.rate_limits:
            if not any([rate_limit['unlimited'], rate_limit['number']]):
                continue

            line = "\nlogging rate-limit" if lines != "" else "logging rate-limit"

            if rate_limit['unlimited']:
                line += " unlimited"
            else:
                line += " {}".format(rate_limit['number'])

            if rate_limit['interval']:
                line += " {}".format(rate_limit['interval'])

            if rate_limit['message']:
                line += " message {}".format(rate_limit['message'])
                lines += line
                continue

            if rate_limit['level']:
                line += " level {}".format(rate_limit['level'])
                lines += line

        return lines

    def generate_recipient_addresses_config(self):
        if not self.recipient_addresses or len(self.recipient_addresses) == 0:
            return ""

        lines = ""

        for recipient in self.recipient_addresses:
            if not recipient['email']:
                continue

            line = "\n" if lines != "" else ""
            line += "logging recipient-address {}".format(recipient['email'])

            if recipient['level']:
                line += " level {}".format(recipient['level'])

            lines += line

        return lines

    @property
    def config(self):
        config = ""

        order = [
            'enable', 'timestamp', 'standby', 'emblem', 'lists', 'buffer_size',
            'console', 'monitor', 'buffered', 'trap', 'history', 'asdm',
            'mail', 'from_address', 'recipient_addresses', 'facility',
            'queue', 'device_id', 'hosts', 'debug_trace', 'flash_bufferwrap',
            'flash_minimum_free', 'flash_maximum_allocation', 'ftp_bufferwrap',
            'ftp_server', 'permit_hostdown', 'classes', 'messages',
            'rate_limits']

        level_parsing = [
            'asdm', 'buffered', 'console', 'history',
            'mail', 'monitor', 'trap']

        for field in order:
            value = None

            if field not in ['ftp_server']:
                value = getattr(self, field)

            if value:
                try:
                    default = object.__getattribute__(self, field).default
                except Exception:
                    default = None

                if default and value == default:
                    continue

                initial = self.initial_values.get(field)

                if self.onlyshowchanges and initial and value == initial:
                    continue

            line = "\n" if config != "" else ""

            if field in level_parsing:
                line += self.generate_level_config(field)
            elif field == 'classes':
                line += self.generate_classes_config()
            elif field == 'ftp_server':
                line += self.generate_ftp_server_config()
            elif field == 'hosts':
                line += self.generate_hosts_config()
            elif field == 'lists':
                line += self.generate_lists_config()
            elif field == 'messages':
                line += self.generate_messages_config()
            elif field == 'rate_limits':
                line += self.generate_rate_limits_config()
            elif field == 'recipient_addresses':
                line += self.generate_recipient_addresses_config()
            elif isinstance(value, bool) and value:
                line += "logging {}".format(field.replace('_', '-'))
            elif not isinstance(value, bool) and value:
                line += "logging {} {}".format(field.replace('_', '-'), str(value))

            if line not in ["\n", ""]:
                config += line

        if config == "":
            return None

        return config
