from configparity.models import Model
from configparity.models.cisco import COMMENTS
from configparity.fields.common import AllowedField
from configparity.fields.common import BoolField
from configparity.fields.common import IntField
from configparity.fields.common import DictField
from configparity.fields.common import ListField
from configparity.fields.common import StrField
from configparity.fields.common import TupleField
from configparity.fields.networking import IPAddressField
from configparity.fields.networking import IPNetworkField
from configparity.fields.networking import MACAddressField
from configparity.fields.networking import VLANField


class Interface(Model):
    authentication_keys = ListField(default=[], list_type=DictField())
    authentication_modes = ListField(default=[], list_type=DictField())
    channel_group = IntField()
    channel_group_mode = StrField(allowed=['active', 'on', 'passive'])
    channel_group_vss_id = IntField()
    ddns = StrField()
    delay = IntField()
    description = StrField()
    dhcp_client_route_distance = IntField()
    dhcp_client_route_track = IntField()
    dhcp_client_update_dns_server = StrField(allowed=['both', 'none'])
    dhcprelay_information_trusted = BoolField()
    dhcprelay_interface_timeout = IntField(low=0)
    dhcprelay_server = AllowedField([IPAddressField(), StrField()])
    duplex = StrField(default='auto', allowed=['auto', 'half', 'full'])
    flowcontrol = DictField()
    hello_intervals = ListField(default=[], list_type=DictField())
    hold_times = ListField(default=[], list_type=DictField())
    igmp = DictField()
    interface = IntField(low=0, readonly=True)
    ipv4_address = AllowedField([IPAddressField(), StrField()])
    ipv4_dhcp = BoolField()
    ipv4_subnet_mask = StrField()
    ipv4_pppoe = BoolField()
    ipv4_standby = AllowedField([IPAddressField(), StrField()])
    ipv6_address = AllowedField([IPAddressField(), StrField()])
    ipv6_enable = BoolField(default=False)
    ipv6_link_local_address = AllowedField([IPAddressField(), StrField()])
    ipv6_link_local_network = IPNetworkField(strict=False)
    ipv6_link_local_standby = AllowedField([IPAddressField(), StrField()])
    ipv6_nd = DictField()
    ipv6_network = IPNetworkField(strict=False)
    ipv6_ospf = DictField()
    ipv6_standby = AllowedField([IPAddressField(), StrField()])
    lacp_port_priority = IntField(low=1, high=65535)
    line_status = StrField(allowed=['down', 'up'])
    mac_address = MACAddressField(splitter=".", split_at=4)
    mac_address_cluster_pool = StrField()
    management_only = BoolField()
    member_interfaces = ListField(default=[], list_type=StrField())
    mfib_forwarding = BoolField()
    multicast_boundaries = ListField(default=[], list_type=DictField())
    nameif = StrField()
    ospf = DictField()
    pim = DictField()
    pppoe_client_route_distance = IntField()
    pppoe_client_route_track = IntField()
    pppoe_client_secondary_track = IntField()
    pppoe_client_vpdn_group = StrField()
    rip_authentication_key = StrField()
    rip_authentication_mode = StrField()
    rip_receive_version = TupleField(default=(None, None), tuple_type=IntField(low=1, high=2))
    rip_send_version = TupleField(default=(None, None), tuple_type=IntField(low=1, high=2))
    security_level = IntField(low=0, high=100)
    shutdown = BoolField(default=False)
    slot = IntField(low=0, readonly=True)
    speed = AllowedField([IntField(low=0), StrField(default='auto', allowed=['auto'])])
    split_horizons = ListField(default=[], list_type=DictField())
    summary_addresses = ListField(default=[], list_type=DictField())
    type = StrField(readonly=True)
    vlan = VLANField(readonly=True)

    def __repr__(self):
        return f"Interface('{self.interface_name}')"

    def __str__(self):
        return self.interface_name

    @staticmethod
    def parse_authentication_config(config, line):
        if line[1] == 'key':
            if 'authentication_keys' not in config:
                config['authentication_keys'] = []

            config['authentication_keys'].append({
                'eigrp': line[3],
                'key': line[4],
                'key-id': line[6]})

        elif line[1] == 'mode':
            if 'authentication_modes' not in config:
                config['authentication_modes'] = []

            config['authentication_modes'].append({
                'eigrp': line[3],
                'md5': 'md5' in line})

        return config

    @staticmethod
    def parse_channel_group_config(config, line):
        config['channel_group'] = line[1]

        if 'mode' in line:
            config['channel_group_mode'] = line[3]

        if 'vss-id' in line:
            config['channel_group_vss_id'] = line[5]

        return config

    @staticmethod
    def parse_dhcp_config(config, line):
        key_items = ['client', 'route', 'update', 'distance', 'track', 'dns', 'server']
        key = 'dhcp'

        for item in line[1:]:
            if item in key_items:
                key += '_' + item
            else:
                config[key] = item

        return config

    @staticmethod
    def parse_dhcprelay_config(config, line):
        key_items = ['information', 'trusted', 'interface', 'timeout', 'server']
        key = 'dhcprelay'

        for item in line[1:]:
            if item in key_items:
                key += '_' + item

                if item == 'trusted':
                    config[key] = True
            else:
                config[key] = item

        return config

    @staticmethod
    def parse_flowcontrol_config(config, line):
        if 'flowcontrol' not in config:
            config['flowcontrol'] = {}

        if 'noconfirm' in line:
            config['flowcontrol']['noconfirm'] = True

        line = [i for i in line[1:] if i not in ['noconfirm', 'send', 'on']]

        if len(line) > 2:
            config['flowcontrol']['low_water'] = line[0]
            config['flowcontrol']['high_water'] = line[1]
            config['flowcontrol']['pause_time'] = line[2]

        return config

    @staticmethod
    def parse_hello_interval_config(config, line):
        if line[0] == 'hello-interval':
            if 'hello_intervals' not in config:
                config['hello_intervals'] = []

            config['hello_intervals'].append({
                'eigrp': line[2],
                'seconds': line[3]})

        return config

    @staticmethod
    def parse_hold_time_config(config, line):
        if line[0] == 'hold-time':
            if 'hold_times' not in config:
                config['hold_times'] = []

            config['hold_times'].append({
                'eigrp': line[2],
                'seconds': line[3]})

        return config

    @staticmethod
    def parse_igmp_config(config, line):
        if 'igmp' not in config:
            config['igmp'] = {}

        config['igmp'][line[1]] = line[2]

        return config

    @staticmethod
    def parse_ip_config(config, line):
        line = line[2:]

        for item in line:
            if item in ['dhcp', 'pppoe']:
                config['ipv4_' + item] = True
                continue

            if '.' in item and 'ipv4_address' not in config:
                config['ipv4_address'] = item
            elif '.' in item and 'ipv4_subnet_mask' not in config:
                config['ipv4_subnet_mask'] = item
            elif '.' in item and 'standby' in line and 'ipv4_standby' not in config:
                config['ipv4_standby'] = item

        return config

    @staticmethod
    def parse_ipv6_config(config, line):
        key = 'ipv6_'

        if line[1] == 'address':
            key = key if 'link-local' not in line else key + 'link_local_'

            config[key + 'address'] = line[2].split('/')[0]
            config[key + 'network'] = line[2]

            if 'standby' in line:
                config[key + 'standby'] = line[-1]

            return config

        if line[1] in ['nd', 'ospf']:
            key += line[1]

            if key not in config:
                config[key] = {}

            if len(line[2:]) > 1:
                config[key][line[2]] = " ".join(line[3:])
            else:
                config[key][line[2]] = True

            return config

    @staticmethod
    def parse_lacp_config(config, line):
        config['lacp_port_priority'] = line[2]

        return config

    @staticmethod
    def parse_mac_address_config(config, line):
        if line[1] == 'cluster-pool':
            config['mac_address_cluster_pool'] = line[2]

        else:
            config['mac_address'] = line[1]

        return config

    @staticmethod
    def parse_member_interface_config(config, line):
        if 'member_interfaces' not in config:
            config['member_interfaces'] = []

        config['member_interfaces'].append(line[1])

        return config

    @staticmethod
    def parse_mfib_config(config, line):
        config['mfib_forwarding'] = True

        return config

    @staticmethod
    def parse_multicast_config(config, line):
        if 'multicast_boundaries' not in config:
            config['multicast_boundaries'] = []

        config['multicast_boundaries'].append({
            'acl': line[2],
            'filter-autorp': 'filter-autorp' in line})

        return config

    @staticmethod
    def parse_ospf_config(config, line):
        if 'ospf' not in config:
            config['ospf'] = {}

        if line[1] == 'mtu-ignore':
            config[line[1]] = True
        else:
            config['ospf'][line[1]] = line[2:]

        return config

    @staticmethod
    def parse_pim_config(config, line):
        if 'pim' not in config:
            config['pim'] = {}

        config['pim'][line[1]] = line[2:]

        return config

    @staticmethod
    def parse_pppoe_config(config, line):
        key_items = ['client', 'route', 'secondary', 'distance', 'track', 'vdpn', 'group']
        key = 'pppoe'

        for item in line[1:]:
            if item in key_items:
                key += '_' + item
            else:
                config[key] = item

        return config

    @staticmethod
    def parse_rip_config(config, line):
        key = "_".join(line[0:3])
        config[key] = " ".join(line[3:])

        return config

    @staticmethod
    def parse_split_horizon_config(config, line):
        if 'split_horizons' not in config:
            config['split_horizons'] = []

        config['split_horizons'].append({'eigrp': line[2]})

        return config

    @staticmethod
    def parse_summary_address_config(config, line):
        if 'summary_addresses' not in config:
            config['summary_addresses'] = []

        config['summary_addresses'].append({
            'eigrp': line[2],
            'address': line[3],
            'mask': line[4],
            'distance': line[5]})

        return config

    def load_config(self, config_str):
        config_lines = [(line[1:] if line.startswith(' ') else line) for line in config_str.splitlines()]
        config = {}

        if 'interface' not in config_lines[0]:
            return None

        parsers = [
            'authentication',
            'channel_group',
            'dhcp',
            'dhcprelay',
            'flowcontrol',
            'hello_interval',
            'hold_time',
            'igmp',
            'ip',
            'ipv6',
            'lacp',
            'mac_address',
            'member_interface'
            'mfib',
            'multicast',
            'ospf',
            'pim',
            'pppoe',
            'rip',
            'split_horizon',
            'summary_address']

        for line in config_lines:
            line = line.split(' ')
            field = line[0].replace('-', '_')

            if field in COMMENTS:
                continue

            if field == 'interface':
                if 'Ethernet' in line[1] or 'Management' in line[1]:
                    if 'Ethernet' in line[1]:
                        config['type'] = line[1].split('Ethernet')[0] + 'Ethernet'
                        name = line[1].split('Ethernet')[1]

                    else:
                        config['type'] = line[1].split('Management')[0] + 'Management'
                        name = line[1].split('Management')[1]

                    config['slot'] = name.split('/')[0]
                    config['interface'] = name.split('/')[1].split('.')[0]
                    config['vlan'] = name.split('/')[1].split('.')[1] if '.' in name else None

                else:
                    config['type'] = line[1]
                    config['interface'] = line[2]

                continue

            if field in parsers:
                func = 'parse_' + field + '_config'
                config = getattr(self, func)(config, line)
                continue

            if len(line) > 1 and field != 'no':
                if field in config and isinstance(config[field], list):
                    config[field].append(" ".join(line[1:]))
                else:
                    config[field] = " ".join(line[1:])
            elif field != 'no':
                config[field] = True

        self.load_dict(**config)

    @property
    def interface_name(self):
        line = ""

        valid_ethernet = all([
            any([
                self.type and 'Ethernet' in self.type,
                self.type and 'Management' in self.type]),
            isinstance(self.slot, int),
            isinstance(self.interface, int)])

        valid_other = all([
            self.type,
            any([
                self.type and 'redundant' in self.type,
                self.type and 'port-channel' in self.type]),
            isinstance(self.interface, int)])

        if valid_ethernet:
            line = f"{self.type}{self.slot}/{self.interface}"

            if self.vlan:
                line += f'.{self.vlan}'

        elif valid_other:
            line = f"{self.type} {self.interface}"

        return line

    @property
    def is_valid(self):
        return self.interface_name != ""

    @property
    def generate_authentication_keys_config(self):
        if len(self.authentication_keys) == 0:
            return None

        config = []

        for values in self.authentication_keys:
            valid_config = all([
                values.get('eigrp'),
                values.get('key'),
                values.get('key-id')])

            if valid_config:
                config.append(
                    f" authentication key eigrp {values['eigrp']} {values['key']} key-id {values['key-id']}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_authentication_modes_config(self):
        if len(self.authentication_modes) == 0:
            return None

        config = []

        for values in self.authentication_modes:
            valid_config = all([
                values['eigrp'],
                len(values) == 2])

            if valid_config:
                line = f" authentication mode eigrp {values['eigrp']}"

                for key in values:
                    if key != 'eigrp':
                        line += f" {key}"

                config.append(line)

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_channel_group_config(self):
        if not all([self.channel_group, self.channel_group_mode]):
            return None

        line = f" channel-group {self.channel_group} mode {self.channel_group_mode}"

        if self.channel_group_vss_id:
            line += f" vss-id {self.channel_group_vss_id}"

        return line

    @property
    def generate_dhcp_config(self):
        if self.dhcp_client_route_distance is not None:
            return f" dhcp client route distance {self.dhcp_client_route_distance}"

        if self.dhcp_client_route_track is not None:
            return f" dhcp client route track {self.dhcp_client_route_track}"

        if self.dhcp_client_update_dns_server is not None:
            return f" dhcp client update dns server {self.dhcp_client_update_dns_server}"

        return None

    @property
    def generate_dhcprelay_config(self):
        if self.dhcprelay_information_trusted:
            return " dhcprelay information trusted"

        if self.dhcprelay_interface_timeout is not None:
            return f" dhcprelay interface timeout {self.dhcprelay_interface_timeout}"

        if self.dhcprelay_server is not None:
            return f" dhcprelay server {self.dhcprelay_server}"

        return None

    @property
    def generate_flowcontrol_config(self):
        valid_flowcontrol = all([
            self.flowcontrol and 'low_water' in self.flowcontrol,
            self.flowcontrol and 'high_water' in self.flowcontrol,
            self.flowcontrol and 'pause_time' in self.flowcontrol])

        if not valid_flowcontrol:
            return None

        line = f" flowcontrol {self.flowcontrol['low_water']}"
        line += f" {self.flowcontrol['high_water']}"
        line += f" {self.flowcontrol['pause_time']}"

        if self.flowcontrol.get('noconfirm'):
            line += " noconfirm"

        return line

    @property
    def generate_hello_intervals_config(self):
        if len(self.hello_intervals) == 0:
            return None

        config = []

        for values in self.hello_intervals:
            valid_config = all([
                'eigrp' in values,
                'seconds' in values])

            if valid_config:
                config.append(f" hello-interval eigrp {values['eigrp']} {values['seconds']}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_hold_times_config(self):
        if len(self.hold_times) == 0:
            return None

        config = []

        for values in self.hold_times:
            valid_config = all([
                'eigrp' in values,
                'seconds' in values])

            if valid_config:
                config.append(f" hold-time eigrp {values['eigrp']} {values['seconds']}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_igmp_config(self):
        if not self.igmp:
            return None

        config = []

        for key, value in self.igmp.items():
            config.append(f" igmp {key} {value}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_ipv4_config(self):
        line = " ip address"

        if not all([self.ipv4_address, self.ipv4_subnet_mask]):
            if self.onlyshowchanges:
                return None

            return " no" + line

        line += f" {self.ipv4_address} {self.ipv4_subnet_mask}"

        if self.ipv4_standby:
            line += f" standby {self.ipv4_standby}"

        return line

    @property
    def generate_ipv6_config(self):
        lines = []

        if self.ipv6_enable:
            lines.append(' ipv6 enable')

        if all([self.ipv6_link_local_address, self.ipv6_link_local_network]):
            line = f" ipv6 {self.ipv6_link_local_address} {self.ipv6_link_local_network.prefixlen}"

            if self.ipv6_link_local_standby:
                line += f" standby {self.ipv6_link_local_standby}"

            lines.append(line)

        if all([self.ipv6_address, self.ipv6_network]):
            line = f" ipv6 {self.ipv6_address}/{self.ipv6_network.prefixlen}"

            if self.ipv6_standby:
                line += f" standby {self.ipv6_standby}"

            lines.append(line)

        for field in ['nd', 'ospf']:
            if f'ipv6_{field}' in self.values:
                values = self.values[f'ipv6_{field}']

                for key in values:
                    value = values[key]

                    if not value:
                        continue

                    line = f" ipv6 {field} {key}"

                    if not isinstance(value, bool):
                        line += f" {value}"

                    lines.append(line)

        if len(lines) == 0:
            return None

        return "\n".join(lines)

    @property
    def generate_lacp_port_priority_config(self):
        if not self.lacp_port_priority:
            return None

        return f" lacp port-priority {self.lacp_port_priority}"

    @property
    def generate_mac_address_config(self):
        if not self.mac_address:
            return None

        return f" mac-address {self.mac_address}"

    @property
    def generate_mac_address_cluster_pool_config(self):
        if not self.mac_address_cluster_pool:
            return None

        return f" mac-address cluster-pool {self.mac_address_cluster_pool}"

    @property
    def generate_member_interfaces_config(self):
        if len(self.member_interfaces) == 0:
            return None

        config = []

        for interface in self.member_interfaces:
            config.append(f" member-interface {interface}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_mfib_forwarding_config(self):
        if not self.mfib_forwarding:
            return None

        return " mfib forwarding"

    @property
    def generate_multicast_boundaries_config(self):
        if len(self.multicast_boundaries) == 0:
            return None

        config = []

        for boundary in self.multicast_boundaries:
            if 'acl' not in boundary:
                continue

            line = f" multicast boundary {boundary['acl']}"

            if boundary.get('filter-autorp'):
                line += ' filter-autorp'

            config.append(line)

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_ospf_config(self):
        if not self.ospf:
            return None

        config = []

        for key, value in self.ospf.items():
            line = f" ospf {key}"

            if not isinstance(value, bool):
                line += f" {value}"

            config.append(line)

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_pim_config(self):
        if not self.pim:
            return None

        config = []

        for key, value in self.pim.items():
            config.append(f" pim {key} {value}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_pppoe_config(self):
        config = []

        if self.pppoe_client_route_distance:
            config.append(f" pppoe client route distance {self.pppoe_client_route_distance}")

        if self.pppoe_client_route_track:
            config.append(f" pppoe client route track {self.pppoe_client_route_track}")

        if self.pppoe_client_secondary_track:
            config.append(f" pppoe client secondary track {self.pppoe_client_secondary_track}")

        if self.pppoe_client_vpdn_group:
            config.append(f" pppoe client vpdn group {self.pppoe_client_vpdn_group}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_rip_config(self):
        config = []

        if self.rip_authentication_key:
            config.append(f" rip authentication key {self.rip_authentication_key}")

        if self.rip_authentication_mode:
            config.append(f" rip authentication mode {self.rip_authentication_mode}")

        if self.rip_receive_version and self.rip_receive_version != (None, None):
            rip_recieve_version = " ".join([i for i in self.rip_receive_version if i])
            config.append(f" rip receive version {rip_recieve_version}")

        if self.rip_send_version and self.rip_send_version != (None, None):
            rip_send_version = " ".join([i for i in self.rip_send_version if i])
            config.append(f" rip send version {rip_send_version}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_split_horizons_config(self):
        if len(self.split_horizons) == 0:
            return None

        config = []

        for values in self.split_horizons:
            value = values.get('eigrp')

            if value:
                config.append(f" split-horizon eigrp {value}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def generate_summary_addresses_config(self):
        if len(self.summary_addresses) == 0:
            return None

        config = []

        for values in self.summary_addresses:
            eigrp = values.get('eigrp')
            address = values.get('address')
            mask = values.get('mask')
            distance = values.get('distance')

            if all([eigrp, address, mask, distance]):
                config.append(f" summary-address eigrp {eigrp} {address} {mask} {distance}")

        if len(config) == 0:
            return None

        return "\n".join(config)

    @property
    def config(self):
        config = f'interface {self.interface_name}'

        generators = [
            'authentication_keys',
            'authentication_modes',
            'channel_group',
            'dhcp',
            'dhcprelay',
            'flowcontrol',
            'hello_intervals',
            'hold_times',
            'igmp',
            'ipv4',
            'ipv6',
            'lacp_port_priority',
            'mac_address',
            'mac_address_cluster_pool',
            'member_interfaces',
            'mfib_forwarding',
            'multicast_boundaries',
            'ospf',
            'pim',
            'pppoe',
            'rip',
            'split_horizons',
            'summary_addresses']

        order = [
            'description',
            'shutdown',
            'vlan',
            'channel_group',
            'speed',
            'duplex',
            'nameif',
            'security_level',
            'mac_address',
            'mac_address_cluster_pool',
            'ipv4',
            'ipv6',
            'authentication_keys'
            'authentication_modes',
            'dhcp',
            'dhcprelay',
            'flowcontrol',
            'hello_intervals',
            'hold_times',
            'igmp',
            'lacp_port_priority',
            'member_interfaces',
            'mfib_forwarding',
            'multicast_boundaries',
            'ospf',
            'pim',
            'pppoe',
            'rip',
            'split_horizons',
            'summary_addresses']

        for field in order:
            if field in generators:
                func = 'generate_' + field + '_config'
                line = getattr(self, func)

                if line:
                    config += f"\n{line}"

                continue

            value = self.values.get(field)
            field = field.replace('_', '-')

            if value is None:
                if field in ['nameif', 'security-level'] and not self.onlyshowchanges:
                    config += f"\n no {field}"

                continue

            config += f"\n {field}"

            if not isinstance(value, bool):
                config += f" {str(value)}"

        if config == f'interface {self.interface_name}':
            return ""

        return config
