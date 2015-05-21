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
'module'            : 'ldapcherry.backend.ldap',
'groupdn'           : 'ou=group,dc=example,dc=org',
'userdn'            : 'ou=People,dc=example,dc=org',
'binddn'            : 'cn=dnscherry,dc=example,dc=org',
'password'          : 'password',
'uri'               : 'ldap://ldap.ldapcherry.org:390',
'ca'                : './tests/test_env/etc/ldapcherry/TEST-cacert.pem',
'starttls'          : 'off',
'checkcert'         : 'off',
'user_filter_tmpl'  : '(uid=%(username)s)',
'group_filter_tmpl' : '(member=%(userdn)s)',
}

cherrypy.log.error = syslog_error

class TestError(object):

    def testNominal(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True

    def testConnect(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        ldap = inv._connect()
        ldap.simple_bind_s(inv.binddn, inv.bindpassword)
        return True

    def testConnectSSL(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
        cfg2['checkcert'] = 'on'
        inv = Backend(cfg2, cherrypy.log, 'ldap')
        ldap = inv._connect()
        ldap.simple_bind_s(inv.binddn, inv.bindpassword)

    def testConnectSSLWrongCA(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
        cfg2['checkcert'] = 'on'
        cfg2['ca'] = './cfg/wrong_ca.crt'
        inv = Backend(cfg2, cherrypy.log, 'ldap')
        ldapc = inv._connect()
        try:
            ldapc.simple_bind_s(inv.binddn, inv.bindpassword)
        except SERVER_DOWN as e:
            assert e[0]['info'] == 'TLS: hostname does not match CN in peer certificate'

#    def testConnectSSLNoCheck(self):
#        cfg2 = cfg.copy()
#        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
#        cfg2['checkcert'] = 'off'
#        inv = Backend(cfg2, cherrypy.log, 'ldap')
#        ldap = inv._connect()
#        ldap.simple_bind_s(inv.binddn, inv.bindpassword)

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        ret = inv.auth('jwatson', 'passwordwatson')
        assert ret == True

    def testAuthFailure(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        res = inv.auth('notauser', 'password') or inv.auth('jwatson', 'notapassword')
        assert res == False

    def testMissingParam(self):
        cfg2 = {}
        return True
        try:
            inv = Backend(cfg2, cherrypy.log, 'ldap')
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True
