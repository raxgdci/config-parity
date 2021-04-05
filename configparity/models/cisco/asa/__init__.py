from importlib import import_module
from pkgutil import iter_modules
from os import path
from configparity.models import Model
from configparity.models.cisco import COMMENTS
from configparity.models.cisco import READONLY
from configparity.fields.common import BoolField
from configparity.fields.common import StrField
from configparity.fields.common import ListField
from configparity.fields.common import ModelField
from configparity.fields.hardware import BytesField


class ASA(Model):
    access_group = ListField(list_type=ModelField('cisco.asa.access_group.AccessGroup', 'asa'))
    access_list = ModelField('cisco.asa.access_list.AccessList', 'asa')
    asa_version = StrField()
    banner = ListField(list_type=ModelField('cisco.asa.banner.Banner', 'asa'))
    cryptochecksum = StrField()
    cpu = StrField()
    domain_name = StrField()
    enable = ModelField('cisco.asa.enable.Enable', 'asa')
    hardware = StrField()
    hostname = StrField(default='ciscoasa')
    interface = ListField(list_type=ModelField('cisco.asa.interface.Interface', 'asa'))
    ip = ModelField('cisco.asa.ip.IP', 'asa')
    model = StrField()
    name = ListField(list_type=ModelField('cisco.asa.name.Name', 'asa'))
    names = BoolField(default=False)
    nat = ListField(list_type=ModelField('cisco.asa.nat.Nat', 'asa'))
    object = ListField(list_type=ModelField('cisco.asa.object.Object', 'asa'))
    object_group = ListField(list_type=ModelField('cisco.asa.object_group.ObjectGroup', 'asa'))
    passwd = ModelField('cisco.asa.passwd.Passwd', 'asa')
    ram = BytesField()
    route = ListField(list_type=ModelField('cisco.asa.route.Route', 'asa'))
    serial_number = StrField()
    # terminal_width = AllowedField([
    #     IntField(low=40, high=511, default=80),
    #     IntField(low=0, high=0)])

    MATCH_TWO = (
        'access_group',
        'name')

    FIELD_ORDER = (
        'serial_number',
        'model',
        'ram',
        'cpu',
        'asa_version',
        # 'terminal',
        'hostname',
        'domain_name',
        'enable',
        'passwd',
        'names',
        'name',
        'interface',
        'banner',
        # 'ftp',
        # 'dns',
        'object',
        'object_group',
        'access_list',
        # 'pager',
        # 'logging',
        # 'mtu',
        'ip',
        # 'failover',
        # 'icmp',
        # 'asdm',
        # 'arp',
        'nat',
        'access_group',
        'route',
        # 'timeout',
        # 'aaa_server',
        # 'user-identity',
        # 'aaa',
        # 'http',
        # 'snmp-server',
        # 'sysopt',
        # 'service',
        # 'crypto',
        # 'telnet',
        # 'ssh',
        # 'console',
        # 'threat-detection',
        # 'ntp',
        # 'dynamic_access_policy_record',
        # 'user',
        # 'class_map',
        # 'policy_map',
        # 'service_policy',
        # 'prompt',
        # 'call_home',
        'cryptochecksum')

    READONLY_FIELDS = (
        'serial_number',
        'model',
        'ram',
        'cpu',
        'asa_version',
        'cryptochecksum')

    def __repr__(self):
        return f"ASA('{self.hostname}')"

    def __str__(self):
        return self.config

    @staticmethod
    def parse_readonly(line):
        line = line[2:] if line.startswith(': ') else line

        if "Serial Number" in line:
            serial_number = line.replace('Serial Number: ', '')

            return {"serial_number": [f"serial_number {serial_number}"]}

        if "ASA Version" in line:
            asa_version = line.split(' ')[2]

            return {"asa_version": [f"asa_version {asa_version}"]}

        if 'Cryptochecksum' in line:
            cryptochecksum = line.split(':')[-1].replace(' ', '')

            return {"cryptochecksum": [f"cryptochecksum {cryptochecksum}"]}

        if "Hardware" in line:
            parts = line.split(', ')
            model = parts[0].replace(' ', '').replace('Hardware:', '')
            ram = parts[1].replace('RAM',  '').replace(' ', '')
            cpu = ", ".join(parts[2:])[4:]

            return {
                "model": [f"model {model}"],
                "ram": [f"ram {ram}"],
                "cpu": [f"cpu {cpu}"]}

        return dict()

    def _parse_config_chunks(self, config_str):
        chunks = {}
        chunk = ""
        last_field = None
        last_subfield = None
        last_indented = False

        for line in config_str.split('\n'):
            indented = line.startswith(' ')
            words = [word for word in line.split(' ') if word != '']
            field = None
            subfield = None

            if len(words) == 0 or line[0] in COMMENTS:
                continue

            readonly = bool(sum(1 for match in READONLY if line.startswith(match)))

            if readonly:
                readonly_chunks = self.parse_readonly(line)

                for this_field, this_line in readonly_chunks.items():
                    chunks[this_field] = this_line

                continue

            if len(words) > 0 and not indented:
                field = words[1] if words[0] == 'no' and len(words) > 1 else words[0]

            field = field.replace('-', '_') if field else None

            if field in self.MATCH_TWO and len(words) >= 2:
                subfield = words[2] if words[0] == 'no' and len(words) > 2 else words[1]

            new_group = any([
                len(words) == 0,
                len(words) > 0 and field and field != last_field,
                len(words) > 1 and subfield and subfield != last_subfield,
                len(words) > 0 and not indented and last_indented])

            if new_group:
                if chunk != "":
                    if last_field not in chunks:
                        chunks[last_field] = []

                    chunks[last_field].append(chunk)
                    chunk = ""

            last_indented = indented

            if field:
                last_field = field

            if subfield:
                last_subfield = field

            chunk += f"\n{line}" if chunk != "" else line

        return chunks

    def load_config(self, config_str):
        config_chunks = self._parse_config_chunks(config_str)

        config = {}

        for field in self.FIELD_ORDER:
            value = config_chunks.get(field)

            if value:
                field_instance = self.get_field_instance(field)

                if not isinstance(field_instance, ListField):
                    value = '\n'.join(value)

                if isinstance(field_instance, BoolField):
                    value = False if value.startswith("no ") else True

                if isinstance(field_instance, StrField) or isinstance(field_instance, BytesField):
                    value = ' '.join(value.split(' ')[1:])

            config[field] = value

        self.load_dict(**config)

    @property
    def is_valid(self):
        return False

    @property
    def only_changes(self):
        config = ""

        for field in self.FIELD_ORDER:
            if field in self.READONLY_FIELDS:
                continue

            current_value = self.values.get(field)
            initial_value = self.initial_values.get(field)
            command = field.replace("_", "-")
            field_instance = self.get_field_instance(field)
            add = ""

            if isinstance(field_instance, ListField):
                for instance in current_value or []:
                    if hasattr(instance, 'is_model') and instance.is_model:
                        this_config = instance.only_changes or ""
                    else:
                        this_config = f"{instance}"

                    add += this_config if add == "" else f"\n{this_config}"

            if isinstance(field_instance, BoolField):
                if current_value and current_value != initial_value:
                    add = command

                if initial_value and not current_value:
                    add = f'no {command}'

            if isinstance(field_instance, StrField):
                if current_value and current_value != initial_value:
                    add = f'{command} {current_value}'

                if initial_value and not current_value:
                    add = f'no {command} {current_value}'

            if isinstance(field_instance, ModelField):
                if instance := current_value:
                    add = instance.only_changes or ""

            if add:
                config += add if config == "" else f"\n{add}"

        return config

    @property
    def config(self):
        config = ""

        for field in self.FIELD_ORDER:
            if field in self.READONLY_FIELDS:
                continue

            add = ""
            field_instance = self.get_field_instance(field)
            current = self.values.get(field)
            key = field.replace("_", "-")

            if isinstance(field_instance, ListField):
                for instance in current or []:
                    this_config = instance.config
                    add += this_config if add == "" else f"\n{this_config}"

            if isinstance(field_instance, BoolField):
                add = key

            if isinstance(field_instance, StrField):
                add = f'{key} {current}'

            if isinstance(field_instance, ModelField):
                if instance := current:
                    add = instance.config

            if add:
                config += add if config == "" else f"\n{add}"

        return config


"""
This fancy code automatically imports modules from the files
in the models/cisco/asa folder upon initialization.
"""
modules = []

for (_, name, _) in iter_modules([path.dirname(__file__)]):
    modules.append(name)
    imported_module = import_module('.' + name, package='configparity.models.cisco.asa')
    class_name = list(filter(lambda x: not x.startswith('__'), dir(imported_module)))

del import_module
del iter_modules
del path
del imported_module
del class_name
