#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
import subprocess
from tempfile import NamedTemporaryFile as tempfile
import re

from sets import Set
from ldapcherry import LdapCherry
from ldapcherry.exceptions import *
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError
import cherrypy
from cherrypy.process import plugins, servers
from cherrypy import Application
import logging
from ldapcherry.lclogging import *
import json

cherrypy.session = {}

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

class HtmlValidationFailed(Exception):
    def __init__(self, out):
        self.errors = out

def htmlvalidator(page):
    f = tempfile()
    stdout = tempfile()
    f.write(page.encode("utf-8"))
    f.seek(0)
    ret = subprocess.call(['./tests/html_validator.py', '-h', f.name], stdout=stdout)
    stdout.seek(0)
    out = stdout.read()
    f.close()
    stdout.close()
    print(out)
    if not re.search(r'Error:.*', out) is None:
        raise HtmlValidationFailed(out)

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

    def testAuth(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        app.auth_mode = 'and'
        ret1 = app._auth('jsmith', 'passwordsmith')
        app.auth_mode = 'or'
        ret2 = app._auth('jsmith', 'passwordsmith')
        assert ret2 == {'connected': True, 'isadmin': False} and \
            ret1 == {'connected': True, 'isadmin': False}

    def testPPolicy(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        wrong = app._checkppolicy('password')['match']
        good = app._checkppolicy('Passw0rd.')['match']
        assert wrong == False and good == True

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

    def testLogin(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        app.auth_mode = 'or'
        try:
            app.login('jwatsoné', 'passwordwatsoné')
        except cherrypy.HTTPRedirect as e:
            expected = 'http://127.0.0.1:8080/'
            assert e[0][0] == expected
        else:
            raise AssertionError("expected an exception")

    def testLoginFailure(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        app.auth_mode = 'or'
        try:
            app.login('jwatsoné', 'wrongPasswordé')
        except cherrypy.HTTPRedirect as e:
            expected = 'http://127.0.0.1:8080/signin'
            assert e[0][0] == expected
        else:
            raise AssertionError("expected an exception")

    def testSearch(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        expected = {
            u'ssmith': {
                'password': u'passwordsmith',
                'cn': u'Sheri Smith',
                'name': u'smith',
                'uid': u'ssmith',
                'email': [u's.smith@example.com',
                          u'ssmith@example.com',
                          u'sheri.smith@example.com'
                     ],
                },
            u'jsmith': {
                'password': u'passwordsmith',
                'cn': u'John Smith',
                'name': u'Smith',
                'uid': u'jsmith',
                'email': [
                    'j.smith@example.com',
                    'jsmith@example.com',
                    'jsmith.smith@example.com'
                    ],
                }
            }
        ret = app._search('smith')
        assert expected == ret

    def testGetUser(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        expected = {
            'password': u'passwordsmith',
            'cn': u'Sheri Smith',
            'uid': u'ssmith',
            'name': u'smith',
            'email': [u's.smith@example.com',
                     u'ssmith@example.com',
                     u'sheri.smith@example.com'
                ],
            }
        ret = app._get_user('ssmith')
        assert expected == ret

    def testAddUser(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        form = {'groups': {}, 'attrs': {'password1': u'password☭', 'password2': u'password☭', 'cn': u'Test ☭ Test', 'name': u'Test ☭', 'uidNumber': u'1000', 'gidNumber': u'1000', 'home': u'/home/test', 'first-name': u'Test ☭', 'email': u'test@test.fr', 'uid': u'test'}, 'roles': {'admin-lv3': u'on', 'admin-lv2': u'on', 'users': u'on'}}
        app._adduser(form)
        app._deleteuser('test')

    def testParse(self):
        app = LdapCherry()
        form = {'attr.val': 'val', 'role.id': 'id', 'group.ldap.id': 'id'}
        ret = app._parse_params(form)
        expected = {'attrs': {'val': 'val'}, 'roles': {'id': 'id'}, 'groups': {'ldap': ['id']}}
        assert expected == ret

    def testModifUser(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        form = {'groups': {}, 'attrs': {'password1': u'password☭', 'password2': u'password☭', 'cn': u'Test ☭ Test', 'name': u'Test ☭', 'uidNumber': u'1000', 'gidNumber': u'1000', 'home': u'/home/test', 'first-name': u'Test ☭', 'email': u'test@test.fr', 'uid': u'test'}, 'roles': {'admin-lv3': u'on', 'admin-lv2': u'on', 'users': u'on'}}
        app._adduser(form)
        modify_form = { 'attrs': {'first-name': u'Test42 ☭', 'uid': u'test'}, 'roles': { 'admin-lv3': u'on'}}
        app._modify(modify_form)
        app._deleteuser('test')

    def testHtml(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        pages = {
                'signin': app.signin(),
                'index': app.index(),
                'searchuser': app.searchuser('smit'),
                'searchadmin':app.searchadmin('smit'),
                'adduser': app.adduser(),
                'modify':app.modify('jsmith'),
                'selfmodify':app.selfmodify(),
                }
        for page in pages:
            print(page)
            htmlvalidator(pages[page])

    def testNoneType(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        app.modify('ssmith'),
 
    def testNaughtyStrings(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry_test.ini', app)
        with open('./tests/cfg/blns.json') as data_file:
            data = json.load(data_file)
        for attr in data:
            print('testing: ' + attr)
            # delete whatever is happening...
            try:
                app._deleteuser('test')
            except:
                pass
            form = {'groups': {}, 'attrs': {'password1': u'password☭', 'password2': u'password☭', 'cn': 'Test', 'name': attr, 'uidNumber': u'1000', 'gidNumber': u'1000', 'home': u'/home/test', 'first-name': u'Test ☭', 'email': u'test@test.fr', 'uid': 'test'}, 'roles': {'admin-lv3': u'on', 'admin-lv2': u'on', 'users': u'on'}}
            app._adduser(form)
            page = app.searchuser('test'),
            app._deleteuser('test')
            htmlvalidator(page[0])

    def testLogger(self):
        app = LdapCherry()
        loadconf('./tests/cfg/ldapcherry.ini', app)
        assert get_loglevel('debug') is logging.DEBUG and \
        get_loglevel('notice') is logging.INFO and \
        get_loglevel('info') is logging.INFO and \
        get_loglevel('warning') is logging.WARNING and \
        get_loglevel('err') is logging.ERROR and \
        get_loglevel('critical') is logging.CRITICAL and \
        get_loglevel('alert') is logging.CRITICAL and \
        get_loglevel('emergency') is logging.CRITICAL and \
        get_loglevel('notalevel') is logging.INFO

