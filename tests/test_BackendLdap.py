#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.backend.backendLdap import Backend
from ldapcherry import syslog_error
from ldapcherry.exceptions import * 
import cherrypy
from ldap import SERVER_DOWN

cfg = {
'module'             : 'ldapcherry.backend.ldap',
'groupdn'            : 'ou=group,dc=example,dc=org',
'userdn'             : 'ou=People,dc=example,dc=org',
'binddn'             : 'cn=dnscherry,dc=example,dc=org',
'password'           : 'password',
'uri'                : 'ldap://ldap.ldapcherry.org:390',
'ca'                 : './tests/test_env/etc/ldapcherry/TEST-cacert.pem',
'starttls'           : 'off',
'checkcert'          : 'off',
'user_filter_tmpl'   : '(uid=%(username)s)',
'group_filter_tmpl'  : '(member=%(userdn)s)',
'search_filter_tmpl' : '&(uid=%(searchstring)s*)(sn=%(searchstring)s*)',
}

cherrypy.log.error = syslog_error
attr = ['shéll', 'shell', 'cn', 'uid', 'uidNumber', 'gidNumber', 'home', 'userPassword', 'givenName', 'email', 'sn']

class TestError(object):

    def testNominal(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        return True

    def testConnect(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        ldap = inv._connect()
        ldap.simple_bind_s(inv.binddn, inv.bindpassword)
        return True

    def testConnectSSL(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
        cfg2['checkcert'] = 'on'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr)
        ldap = inv._connect()
        ldap.simple_bind_s(inv.binddn, inv.bindpassword)

    def testLdapUnavaible(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://notaldap:637'
        cfg2['checkcert'] = 'on'
        cfg2['ca'] = './cfg/ca.crt'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr)
        ldapc = inv._connect()
        try:
            ldapc.simple_bind_s(inv.binddn, inv.bindpassword)
        except SERVER_DOWN as e:
            return 
        else:
            raise AssertionError("expected an exception")

    def testConnectSSLWrongCA(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
        cfg2['checkcert'] = 'on'
        cfg2['ca'] = './cfg/wrong_ca.crt'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr)
        ldapc = inv._connect()
        try:
            ldapc.simple_bind_s(inv.binddn, inv.bindpassword)
        except SERVER_DOWN as e:
            assert e[0]['info'] == 'TLS: hostname does not match CN in peer certificate'

#    def testConnectSSLNoCheck(self):
#        cfg2 = cfg.copy()
#        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
#        cfg2['checkcert'] = 'off'
#        inv = Backend(cfg2, cherrypy.log, 'ldap', attr)
#        ldap = inv._connect()
#        ldap.simple_bind_s(inv.binddn, inv.bindpassword)

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        return True

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        ret = inv.auth('jwatson', 'passwordwatson')
        assert ret == True

    def testAuthFailure(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        res = inv.auth('notauser', 'password') or inv.auth('jwatson', 'notapassword')
        assert res == False

    def testMissingParam(self):
        cfg2 = {}
        return True
        try:
            inv = Backend(cfg2, cherrypy.log, 'ldap', attr)
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        ret = inv.get_user('jwatson')
        expected = ('cn=John Watson,ou=People,dc=example,dc=org', {'uid': ['jwatson'], 'cn': ['John Watson'], 'sn': ['watson']})
        assert ret == expected
