from configparity.models import Model
from configparity.fields.common import IntField
from configparity.fields.common import ListField
from configparity.fields.common import ModelField


class AccessList(Model):
    alert_interval = IntField(low=1, high=3600, default=300)
    deny_flow_max = IntField(low=1, high=4096, default=4096)
    entries = ListField(list_type=ModelField(
        'cisco.asa.access_control_entry.AccessControlEntry',
        related_name='access_list'))

    def __str__(self):
        return self.config

    def __repr__(self):
        return f"AccessList('{len(self.entries)} Entries')"

    def load_config(self, config_str):
        config_lines = config_str.splitlines()
        config = {'entries': []}

        for line in config_lines:
            line = line.split(' ')

            if line[0] != 'access-list':
                continue

            field = line[1]

            if field not in ['alert-interval', 'deny-flow-max']:
                config['entries'].append(" ".join(line))
                continue

            field = field.replace('-', '_')
            config[field] = line[2]

        self.load_dict(**config)

    @property
    def is_valid(self):
        return self.entries and len(self.entries) > 0

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = ""

        if self.alert_interval and self.alert_interval != 300:
            config += f"access-list alert-interval {self.alert_interval}\n"

        if self.deny_flow_max and self.deny_flow_max != 4096:
            config += f"access-list deny-flow-max {self.deny_flow_max}\n"

        line = 1
        remove_entries = []

        for entry in self.entries:
            entry_config = None

            if self.onlyshowchanges:
                new = entry.config
                initial = entry.initial_config

                if new != initial:
                    new = new.split(' ')
                    new = " ".join(new[0:2]) + f" line {line} " + " ".join(new[2:])

                    remove_entries.append(initial)
                    entry_config = new

            else:
                entry_config = entry.config

            if entry_config:
                config += f"{entry_config}\n"

            line += 1

        if config[-1:] == "\n":
            config = config[:-1]

        for entry in remove_entries:
            config += f"\nno {entry}"

        return config
