from configparity.models import Model
from configparity.fields.common import AllowedField
from configparity.fields.common import BoolField
from configparity.fields.common import IntField
from configparity.fields.common import StrField


class IPAudit(Model):
    interface = StrField()
    specification_name = StrField()
    name = StrField()
    type = StrField(allowed=['attack', 'info'])
    alarm = BoolField(default=False)
    drop = BoolField(default=False)
    reset = BoolField(default=False)
    signature = AllowedField([
        IntField(low=1000, high=1006),
        IntField(low=1100, high=1103),
        IntField(low=2000, high=2012),
        IntField(low=2150, high=2151),
        IntField(low=2154, high=2154),
        IntField(low=3040, high=3042),
        IntField(low=3153, high=3154),
        IntField(low=4050, high=4052),
        IntField(low=6050, high=6053),
        IntField(low=6100, high=6103),
        IntField(low=6150, high=6155),
        IntField(low=6175, high=6175),
        IntField(low=6180, high=6180),
        IntField(low=6190, high=6190)])

    def __repr__(self):
        if self.interface:
            string = "Interface {}".format(self.interface)

        elif self.signature:
            string = "Signature {}".format(self.signature)

        elif self.name:
            string = "{}.{}".format(self.name, self.type)

        else:
            string = self.type

        return "IPAudit('{}')".format(string)

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        config_str = config_str.split(' ')

        is_valid = all([
            config_str[0] == 'ip',
            config_str[1] == 'audit'])

        if not is_valid:
            return None

        config_str = config_str[2:]
        config = {}

        if config_str[0] == 'interface':
            config['interface'] = config_str[1]
            config['specification_name'] = config_str[2]

            self.load_dict(**config)
            return

        if config_str[0] == 'signature' and config_str[2] == 'disable':
            config['signature'] = config_str[1]

            self.load_dict(**config)
            return

        if config_str[0] == 'name':
            config['name'] = config_str[1]
            config_str = config_str[2:]

        config['type'] = config_str[0]

        if 'alarm' in config_str:
            config['alarm'] = True

        if 'drop' in config_str:
            config['drop'] = True

        if 'reset' in config_str:
            config['reset'] = True

        self.load_dict(**config)

    @property
    def is_valid(self):
        return any([
            all([self.interface, self.specification_name]),
            self.signature,
            all([
                self.type,
                any([
                    self.alarm,
                    self.drop,
                    self.reset])])])

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = "ip audit"

        if self.interface:
            return "{} interface {} {}".format(
                config,
                self.interface,
                self.specification_name)

        if self.signature:
            return "{} signature {} disable".format(
                config,
                self.signature)

        if self.name:
            config = "{} name {}".format(
                config,
                self.name)

        config = "{} {} action".format(
            config,
            self.type)

        config = "{} alarm".format(config) if self.alarm else config
        config = "{} drop".format(config) if self.drop else config
        config = "{} reset".format(config) if self.reset else config

        return config
