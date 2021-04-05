from configparity.models import Model
from configparity.fields.common import StrField


class IPVerify(Model):
    reverse_path_interface = StrField()

    def __repr__(self):
        return "IPVerify('{}')".format(self.reverse_path_interface)

    def __str__(self):
        return self.config

    def load_config(self, config_str):
        if 'ip verify reverse-path interface' not in config_str:
            return None

        config_str = config_str.split(' ')

        config = {
            'reverse_path_interface': config_str[4]}

        self.load_dict(**config)

    @property
    def is_valid(self):
        if self.reverse_path_interface:
            return True

        return False

    @property
    def config(self):
        if not self.is_valid:
            return None

        return "ip verify reverse-path interface {}".format(self.reverse_path_interface)
