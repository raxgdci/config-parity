from configparity.models import Model
from configparity.fields.common import AllowedField
from configparity.fields.common import BoolField
from configparity.fields.common import IntField
from configparity.fields.common import StrField
from configparity.fields.common import TimeField
from configparity.fields.networking import IPAddressField
from configparity.fields.networking import IPNetworkField
from configparity.fields.networking import MACAddressField


class Failover(Model):
    failover = BoolField(default=False)
    interface_active_ip = IPAddressField()
    interface_ip_name = StrField()
    interface_network = IPNetworkField(strict=False)
    interface_policy = AllowedField([IntField(low=1, high=110), StrField()])
    interface_standby_ip = IPAddressField()
    ipsec_pre_shared_key = StrField()
    ipsec_pre_shared_key_encrypted = BoolField(default=False)
    key = StrField()
    key_encrypted = BoolField(default=False)
    lan_interface = StrField()
    lan_name = StrField()
    lan_unit = StrField(allowed=['primary', 'secondary'], default='primary')
    link_interface = StrField()
    link_name = StrField()
    mac_address_active = MACAddressField()
    mac_address_name = StrField()
    mac_address_standy = MACAddressField()
    polltime_interface = IntField(low=1, high=15, default=1)
    polltime_interface_msec = IntField(low=500, high=999)
    polltime_interface_holdtime = IntField(low=5, high=75)
    polltime_unit = IntField(low=1, high=15, default=1)
    polltime_unit_msec = IntField(low=200, high=999)
    polltime_unit_holdtime = IntField(low=1, high=45)
    polltime_unit_holdtime_msec = IntField(low=800, high=999)
    replication_http = BoolField(default=False)
    timeout = TimeField('%H:%M:%S')

    def __repr__(self):
        return "Failover('{}')".format(self.lan_unit)

    def __str__(self):
        return self.config

    def _parse_encryption_config(self, line, config):
        if line[1] not in ['ipsec', 'key']:
            return config

        key = line[1]
        value_in = 2

        if line[2] == 'pre-shared-key':
            key += '_pre_shared_key'
            value_in += 1

        if line[value_in] in ['0', '8']:
            if line[value_in] == '8':
                config[key + '_encrypted'] = True

            value_in += 1

        config[key] = line[value_in]

        return config

    def _parse_polltime_config(self, line, config):
        if line[1] != 'polltime':
            return config

        key = 'polltime_interface' if line[2] == 'interface' else 'polltime_unit'
        value = 3 if line[2] in ['interface', 'unit'] else 2
        holdtime_key = key + '_holdtime'

        if line[value] == 'msec':
            value += 1
            key += '_{}'.format('msec')

        config[key] = line[value]

        if line[value + 2] == 'msec':
            holdtime_key += "_msec"
            config[holdtime_key] = line[value + 3]
        else:
            config[holdtime_key] = line[value + 2]

        return config

    def load_config(self, config_str):
        config_lines = config_str.splitlines()
        config = {}

        if 'failover' not in config_lines[0]:
            return None

        for line in config_lines:
            line = line.split(' ')

            if len(line) == 1 and line[0] == 'failover':
                config['failover'] = True

            elif all([len(line) == 2, " ".join(line) == 'no failover']):
                config['failover'] = False

            elif line[1] == 'lan' and line[2] == 'unit':
                config['lan_unit'] = line[3]

            elif line[1] == 'link':
                config['link_interface'] = line[2]
                config['link_name'] = line[3]

            elif line[1] == 'interface' and line[2] == 'ip':
                config['interface_ip_name'] = line[3]

                if '.' in line[4]:
                    config['interface_active_ip'] = line[4]
                    config['interface_network'] = "{}/{}".format(line[4], line[5])
                    config['interface_standby_ip'] = line[7]
                elif ':' in line[4]:
                    config['interface_active_ip'] = line[4].split('/')[0]
                    config['interface_network'] = line[4]
                    config['interface_standby_ip'] = line[6]

            elif line[1] == 'interface-policy':
                config['interface_policy'] = line[2]

            elif line[1] in ['ipsec', 'key']:
                config = self._parse_encryption_config(line, config)

            elif line[1] == 'mac' and line[2] == 'address':
                config['mac_address_active'] = line[4]
                config['mac_address_standy'] = line[5]
                config['mac_address_name'] = line[3]

            elif line[1] == 'polltime':
                config = self._parse_polltime_config(line, config)

            elif line[1] == 'replication' and line[2] == 'http':
                config['replication_http'] = True

            elif line[1] == 'timeout':
                config['timeout'] = line[2]

        if config == {}:
            return None

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([self.link_name, self.link_interface])

    def _generate_key_config(self):
        config = ""

        if self.key and not self.ipsec_pre_shared_key:
            config += "failover key{} {}\n".format(
                " 8" if self.key_encrytped else "",
                self.key)

        return config

    def _generate_ipsec_config(self):
        config = ""

        if self.ipsec_pre_shared_key:
            config += "failover ipsec pre-shared-key{} {}\n".format(
                " 8" if self.ipsec_pre_shared_key_encrypted else "",
                self.ipsec_pre_shared_key)

        return config

    def _generate_polltime_config(self):
        config = ""
        key_parts = ['_unit', '_interface']

        for key_part in key_parts:
            key = "polltime{}".format(key_part)
            polltime = self.values.get(key)
            holdtime = self.values.get(key + "_holdtime")

            if not polltime or polltime == 1:
                msec = self.values.get(key + "_msec")
                polltime = "msec {}".format(msec) if msec else polltime

            if not holdtime:
                msec = self.values.get(key + "_holdtime_msec")
                holdtime = "msec {}".format(msec) if msec else None

            if polltime and holdtime:
                config += "failover polltime{} {} holdtime {}\n".format(
                    key_part.replace('_', ' '),
                    polltime,
                    holdtime)

        return config

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = "failover\n" if self.failover else "no failover\n"

        if self.lan_unit:
            config += "failover lan unit {}\n".format(self.lan_unit)

        if self.interface_policy:
            config += "failover interface-policy {}\n".format(self.interface_policy)

        config += self._generate_polltime_config()
        config += self._generate_key_config()
        config += "failover replication http\n" if self.replication_http else ""
        config += "failover timeout {}\n".format(self.timeout) if self.timeout else ""

        if self.link_name:
            config += "failover link {} {}\n".format(self.link_name, self.link_interface)

        interface = all([
            self.interface_active_ip,
            self.interface_ip_name,
            self.interface_network,
            self.interface_standby_ip])

        if all([interface, ':' in str(self.interface_active_ip)]):
            config += "failover interface ip {} {} standby {}\n".format(
                self.interface_ip_name,
                str(self.interface_active_ip) + "/" + str(self.interface_network.prefixlen),
                self.interface_standby_ip)
        elif interface:
            config += "failover interface ip {} {} {} standby {}\n".format(
                self.interface_ip_name,
                self.interface_active_ip,
                self.interface_network.netmask,
                self.interface_standby_ip)

        if all([self.mac_address_name, self.mac_address_active, self.mac_address_standy]):
            config += "failover mac address {} {} {}\n".format(
                self.mac_address_name,
                self.mac_address_active,
                self.mac_address_standy)

        config += self._generate_ipsec_config()

        return config[:-1]
