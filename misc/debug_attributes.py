from ldapcherry.attributes import Attributes
from ldapcherry.exceptions import DumplicateRoleKey, MissingKey, DumplicateRoleContent, MissingRolesFile
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError
from yaml import load, dump
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class CustomDumper(yaml.SafeDumper):
    "A custom YAML dumper that never emits aliases"

    def ignore_aliases(self, _data):
        return True

inv = Attributes('./conf/attributes.yml')
