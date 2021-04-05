from configparity.models import Model
from configparity.fields.common import ListField
from configparity.fields.common import ModelField


class IP(Model):
    audit = ListField(list_type=ModelField('cisco.asa.ip_audit.IPAudit', 'asa'))
    local = ListField(list_type=ModelField('cisco.asa.ip_local_pool.IPLocalPool', 'asa'))
    verify = ListField(list_type=ModelField('cisco.asa.ip_verify.IPVerify', 'asa'))

    def __str__(self):
        return self.config

    def __repr__(self):
        return f"IP()"

    def load_config(self, config_str):
        config_lines = config_str.splitlines()
        config = {'audit': [], 'local': [], 'verify': []}

        for line in config_lines:
            words = line.split(' ')

            if words[0] != 'ip' or words[1] not in ['audit', 'local', 'verify']:
                continue

            field = words[1]

            config[field].append(line)

        self.load_dict(**config)

    @property
    def is_valid(self):
        is_valid = any([
            self.audit and len(self.audit) > 0,
            self.local and len(self.local) > 0,
            self.verify and len(self.verify) > 0])

        return is_valid

    @property
    def config(self):
        if not self.is_valid:
            return None

        config = ""

        instances = (self.audit or []) + (self.local or []) + (self.verify or [])

        for instance in instances:
            if self.onlyshowchanges:
                if changes := instance.only_changes:
                    config += changes if config == "" else f"\n{changes}"

            else:
                config += instance.config if config == "" else f"\n{instance.config}"

        return config
