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

cfg = {
'module'            : 'ldapcherry.backend.ldap',
'groupdn'           : 'ou=group,dc=example,dc=com',
'people'            : 'ou=group,dc=example,dc=com',
'binddn'            : 'cn=ldapcherry,dc=example,dc=com',
'password'          : 'password',
'uri'               : 'ldaps://ldap.ldapcherry.org',
'ca'                : '/etc/dnscherry/TEST-cacert.pem',
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
        inv._connect()
        return True

    def testConnectSSL(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True

    def testConnectSSLNoCheck(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True

    def testAuthFailure(self):
        inv = Backend(cfg, cherrypy.log, 'ldap')
        return True

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
