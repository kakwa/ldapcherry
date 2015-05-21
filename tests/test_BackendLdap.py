#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.backend.ldap import Backend
from ldapcherry.exceptions import * 
import cherrypy

cfg = {
'module'            : 'ldapcherry.backend.ldap',
'groupdn'           : 'ou=group,dc=example,dc=com',
'people'            : 'ou=group,dc=example,dc=com',
'authdn'            : 'cn=ldapcherry,dc=example,dc=com',
'password'          : 'password',
'uri'               : 'ldaps://ldap.ldapcherry.org',
'ca'                : '/etc/dnscherry/TEST-cacert.pem',
'starttls'          : 'on',
'checkcert'         : 'off',
'user.filter.tmpl'  : '(uid=%(username)s)',
'group.filter.tmpl' : '(member=%(userdn)s)',
}

class TestError(object):

    def testNominal(self):
        inv = Backend(cfg, cherrypy.log)
        return True

    def testConnect(self):
        inv = Backend(cfg, cherrypy.log)
        return True

    def testConnectSSL(self):
        inv = Backend(cfg, cherrypy.log)
        return True

    def testConnectSSLNoCheck(self):
        inv = Backend(cfg, cherrypy.log)
        return True

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log)
        return True

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log)
        return True

    def testAuthFailure(self):
        inv = Backend(cfg, cherrypy.log)
        return True

    def testMissingParam(self):
        cfg2 = {}
        return True
        try:
            inv = Backend(cfg2, cherrypy.log)
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log)
        return True
