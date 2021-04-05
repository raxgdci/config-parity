from configparity.models import Model
from configparity.fields.common import IntField
from configparity.fields.common import StrField
from configparity.fields.networking import IPAddressField
from configparity.fields.networking import IPNetworkField


class Route(Model):
    method = StrField(default='static')
    if_name = StrField()
    route = IPNetworkField()
    next_hop = IPAddressField()
    distance = IntField(low=0)

    def __repr__(self):
        return "Route('{}')".format(self.next_hop)

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        config_str = config_str.split(' ')

        is_valid = any([
            all([
                config_str[0] == 'route',
                len(config_str) >= 5]),
            all([
                " ".join(config_str[0:1]) == 'ipv6 route',
                len(config_str) >= 6])])

        if not is_valid:
            return None

        config = {}

        if config_str[0] == 'route':
            config['if_name'] = config_str[1]
            config['route'] = " ".join(config_str[2:4])
            config['next_hop'] = config_str[4]

            if len(config_str) == 6:
                config['distance'] = config_str[5]

        elif config_str[0] == 'ipv6':
            config['if_name'] = config_str[2]
            config['route'] = " ".join(config_str[3:5])
            config['next_hop'] = config_str[5]

            if len(config_str) == 7:
                config['distance'] = config_str[6]

        is_valid = all([
            'if_name' in config,
            'route' in config and 'next_hop' in config])

        if not is_valid:
            return None

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.if_name,
            self.route and self.next_hop,
            self.distance])

    @property
    def config(self):
        if not self.is_valid or self.method != 'static':
            return None

        route_str = "route " + self.if_name

        if '.' in str(self.next_hop):
            network_str = "{} {}".format(
                self.route.network_address,
                self.route.netmask,
                self.next_hop)
        else:
            route_str = "ipv6 {}".route_str
            network_str = "{} {}".format(self.route, self.next_hop)

        return "{} {} {}".format(route_str, network_str, self.distance)

    @property
    def remove_config(self):
        if not self.config:
            return None

        return "no " + self.config
