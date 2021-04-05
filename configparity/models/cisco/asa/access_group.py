from configparity.models import Model
from configparity.fields.common import StrField


class AccessGroup(Model):
    name = StrField(readonly=True)
    traffic = StrField(readonly=True, allowed=['global', 'in', 'out'])
    if_name = StrField(readonly=True)

    def __str__(self):
        return self.config

    def __repr__(self):
        return "AccessGroup('{}')".format(self.name)

    def load_config(self, config_str):
        config_str = config_str.split(' ')

        is_valid = all([
            config_str[0] == 'access-group',
            len(config_str) == 5])

        if not is_valid:
            return None

        config = {
            'name': config_str[1],
            'traffic': config_str[2],
            'if_name': config_str[4]}

        self.load_dict(**config)

    @property
    def is_valid(self):
        return all([
            self.name,
            self.traffic,
            self.if_name])

    @property
    def config(self):
        if not self.is_valid:
            return None

        return "access-group {} {} interface {}".format(
            self.name,
            self.traffic,
            self.if_name)

    @property
    def remove_config(self):
        if self.config:
            return "no {}".format(self.config)

        return None
