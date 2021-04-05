from configparity.models import Model
from configparity.fields.common import StrField


class Banner(Model):
    asdm = StrField()
    exec = StrField()
    login = StrField()
    motd = StrField()

    def __repr__(self):
        return "Banner('{}')".format(self.banner_type.upper())

    def __str__(self):
        return self.config

    @property
    def banner_type(self):
        banner_type = None

        if self.asdm:
            banner_type = 'asdm'
        elif self.exec:
            banner_type = 'exec'
        elif self.login:
            banner_type = 'login'
        elif self.motd:
            banner_type = 'motd'

        return banner_type

    def load_config(self, config_str):
        lines = config_str.splitlines()
        config = {}
        banner_type = None

        for line in lines:
            line = line.split(' ')
            field = line[0].lower()
            this_banner_type = line[1].lower()

            if not banner_type:
                banner_type = this_banner_type

            elif banner_type != this_banner_type:
                this_banner_type = None

            if field != 'banner' and config == {}:
                return None

            elif field != 'banner' or not this_banner_type:
                break

            line_message = " ".join(line[2:])

            if banner_type not in config:
                config[banner_type] = line_message
            elif banner_type and banner_type in config:
                config[banner_type] += "\n{}".format(line_message)

        self.load_dict(**config)

    @property
    def is_valid(self):
        return self.banner_type is not None

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = []
        banner_type = self.banner_type
        banner = self.values[banner_type].splitlines()

        for line in banner:
            config.append("banner {} {}".format(banner_type, line))

        return "\n".join(config)
