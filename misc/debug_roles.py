from ldapcherry.roles import Roles
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

inv = Roles('./conf/roles.yml')
print 
print inv.dump_nest()

groups = {
'ad' : ['Domain Users', 'Domain Users 2'],
'ldap': ['cn=users,ou=group,dc=example,dc=com']
}

print inv.get_roles(groups)

groups = {
'ad' : ['Domain Users', 'Domain Users 2'],
'ldap': ['cn=users,ou=group,dc=example,dc=com',
    'cn=nagios admins,ou=group,dc=example,dc=com',
    'cn=developpers,ou=group,dc=example,dc=com',
    ],
'toto': ['not a group'],
}


print inv.get_roles(groups)

print inv.get_allroles()

print inv.get_backends()
