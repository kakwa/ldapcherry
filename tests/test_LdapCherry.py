#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry import LdapCherry
from ldapcherry.exceptions import *
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

conf = {'/static': {'tools.staticdir.dir': './resources/static/', 'tools.staticdir.on': True}, 'roles': {'roles.file': './tests/cfg/roles.yml'}, 'global': {'tools.sessions.on': True, 'log.access_handler': 'syslog', 'log.level': 'debug', 'server.thread_pool': 8, 'log.error_handler': 'syslog', 'server.socket_port': 8080, 'server.socket_host': '127.0.0.1', 'tools.sessions.timeout': 10, 'request.show_tracebacks': False}, 'auth': {'auth.mode': 'or'}, 'backends': {'ldap.checkcert': 'off', 'ldap.module': 'ldapcherry.backends.ldap', 'ldap.uri': 'ldaps://ldap.ldapcherry.org', 'ldap.starttls': 'on', 'ldap.groupdn': 'ou=group,dc=example,dc=com', 'ldap.people': 'ou=group,dc=example,dc=com', 'ldap.authdn': 'cn=ldapcherry,dc=example,dc=com', 'ldap.password': 'password', 'ldap.ca': '/etc/dnscherry/TEST-cacert.pem', 'ad.module': 'ldapcherry.backends.ad', 'ad.auth': 'Administrator', 'ad.password': 'password'}, 'attributes': {'attributes.file': './tests/cfg/attributes.yml'}, 'resources': {'templates.dir': './resources/templates/'}}

def loadconf(configfile, instance):
    app = cherrypy.tree.mount(instance, '/', configfile)
    cherrypy.config.update(configfile)
    instance.reload(app.config)

class BadModule():
    pass

class TestError(object):

    def testNominal(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        return True

    def testMissingBackendModule(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        cfg = {'backends': {'ldap.module': 'dontexists'}}
        try:
            app._init_backends(cfg)
        except BackendModuleLoadingFail:
            return
        else:
            raise AssertionError("expected an exception")

    def testInitgBackendModuleFail(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        cfg = {'backends': {'ldap.module': 'ldapcherry.backend'}}
        try:
            app._init_backends(cfg)
        except BackendModuleInitFail:
            return
        else:
            raise AssertionError("expected an exception")



    def testLog(self):
        app = LdapCherry()
        cfg = { 'global' : {}}
        for t in ['none', 'file', 'syslog']:
            cfg['global']['log.access_handler']=t
            cfg['global']['log.error_handler']=t
            app._set_access_log(cfg, logging.DEBUG)
            app._set_error_log(cfg, logging.DEBUG)
        
    def testMissingBackend(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        del app.backends_params['ad']
        try:
            app._check_backends()
        except MissingBackend:
            return
        else:
            raise AssertionError("expected an exception")

    def testMissingParameters(self):
        app = LdapCherry()
        try:
            app.reload({})
        except SystemExit:
            return
        else:
            raise AssertionError("expected an exception")

    def testRandomException(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        e = Exception()
        app._handle_exception(e)

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

