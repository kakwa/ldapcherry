#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

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

class TestError(object):

    def testNominal(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        return True

    def testLogger(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        assert app._get_loglevel('debug') is logging.DEBUG and \
        app._get_loglevel('notice') is logging.INFO and \
        app._get_loglevel('info') is logging.INFO and \
        app._get_loglevel('warning') is logging.WARNING and \
        app._get_loglevel('err') is logging.ERROR and \
        app._get_loglevel('critical') is logging.CRITICAL and \
        app._get_loglevel('alert') is logging.CRITICAL and \
        app._get_loglevel('emergency') is logging.CRITICAL and \
        app._get_loglevel('notalevel') is logging.INFO

