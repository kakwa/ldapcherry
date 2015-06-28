import pytest
import sys
from sets import Set
from ldapcherry import LdapCherry
from ldapcherry.exceptions import DumplicateRoleKey, MissingKey, DumplicateRoleContent, MissingRolesFile, MissingRole
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError
import cherrypy
from cherrypy.process import plugins, servers
from cherrypy import Application
import logging

# monkey patching cherrypy to disable config interpolation
def new_as_dict(self, raw=True, vars=None):
    """Convert an INI file to a dictionary"""
    # Load INI file into a dict
    result = {}
    for section in self.sections():
        if section not in result:
            result[section] = {}
        for option in self.options(section):
            value = self.get(section, option, raw=raw, vars=vars)
            try:
                value = cherrypy.lib.reprconf.unrepr(value)
            except Exception:
                x = sys.exc_info()[1]
                msg = ("Config error in section: %r, option: %r, "
                       "value: %r. Config values must be valid Python." %
                       (section, option, value))
                raise ValueError(msg, x.__class__.__name__, x.args)
            result[section][option] = value
    return result
cherrypy.lib.reprconf.Parser.as_dict = new_as_dict


def loadconf(configfile, instance):
    app = cherrypy.tree.mount(instance, '/', configfile)
    cherrypy.config.update(configfile)
    instance.reload(app.config)

app = LdapCherry()
loadconf('./tests/cfg/ldapcherry.ini', app)
ret = app._get_user('ssmith')
print ret

}

form = {'groups': {}, 'attrs': {'password1': u'password☭', 'password2': u'password☭', 'shell': u'/bin/zsh', 'cn': u'Test ☭ Test', 'name': u'Test ☭', 'uidNumber': u'1000', 'gidNumber': u'1000', 'home': u'/home/test', 'first-name': u'Test ☭', 'email': u'test@test.fr', 'uid': u'test'}, 'roles': {'admin-lv3': u'on', 'admin-lv2': u'on', 'users': u'on'}}
