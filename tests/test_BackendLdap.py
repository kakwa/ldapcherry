#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.backend.backendLdap import Backend, DelUserDontExists
from ldapcherry.exceptions import * 
import cherrypy
import logging
import ldap

cfg = {
'module'             : 'ldapcherry.backend.ldap',
'groupdn'            : 'ou=groups,dc=example,dc=org',
'userdn'             : 'ou=People,dc=example,dc=org',
'binddn'             : 'cn=dnscherry,dc=example,dc=org',
'password'           : 'password',
'uri'                : 'ldap://ldap.ldapcherry.org:390',
'ca'                 : './tests/test_env/etc/ldapcherry/TEST-cacert.pem',
'starttls'           : 'off',
'checkcert'          : 'off',
'user_filter_tmpl'   : '(uid=%(username)s)',
'group_filter_tmpl'  : '(member=%(userdn)s)',
'search_filter_tmpl' : '(|(uid=%(searchstring)s*)(sn=%(searchstring)s*))',
'objectclasses'      : 'top, person, organizationalPerson, simpleSecurityObject, posixAccount',
'dn_user_attr'       : 'uid',
}

def syslog_error(msg='', context='',
        severity=logging.INFO, traceback=False):
    pass

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
        except ldap.SERVER_DOWN as e:
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
        except ldap.SERVER_DOWN as e:
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
        expected = {'uid': 'jwatson', 'cn': 'John Watson', 'sn': 'watson'}
        assert ret == expected

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        ret = inv.get_groups('jwatson')
        expected = ['cn=itpeople,ou=Groups,dc=example,dc=org']
        assert ret == expected

    def testSearchUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        ret = inv.search('smith')
        expected = [('cn=Sheri Smith,ou=People,dc=example,dc=org', {'uid': ['ssmith'], 'objectClass': ['inetOrgPerson'], 'carLicense': ['HERCAR 125'], 'sn': ['smith'], 'mail': ['s.smith@example.com', 'ssmith@example.com', 'sheri.smith@example.com'], 'homePhone': ['555-111-2225'], 'cn': ['Sheri Smith']}), ('cn=John Smith,ou=People,dc=example,dc=org', {'uid': ['jsmith'], 'objectClass': ['inetOrgPerson'], 'carLicense': ['HISCAR 125'], 'sn': ['Smith'], 'mail': ['j.smith@example.com', 'jsmith@example.com', 'jsmith.smith@example.com'], 'homePhone': ['555-111-2225'], 'cn': ['John Smith']})]
        assert ret == expected

    def testAddUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        user = {
        'uid': 'test',
        'sn':  'test',
        'cn':  'test',
        'userPassword': 'test',
        'uidNumber': '42',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        inv.add_user(user)
        inv.del_user('test')

    def testAddUserDuplicate(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        user = {
        'uid': 'test',
        'sn':  'test',
        'cn':  'test',
        'uidNumber': '42',
        'userPassword': 'test',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        try:
            inv.add_user(user)
            inv.add_user(user)
        except ldap.ALREADY_EXISTS:
            inv.del_user('test')
            return
        else:
            inv.del_user('test')
            raise AssertionError("expected an exception")

    def testDelUserDontExists(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        try:
            inv.del_user('test')
            inv.del_user('test')
        except DelUserDontExists:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        ret = inv.get_user('jwatson')
        expected = {'sn': 'watson', 'uid': 'jwatson', 'cn': 'John Watson'}
        assert ret == expected

    def testAddUserMissingMustAttribute(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr)
        user = {
        'uid': 'test',
        'sn':  'test',
        'cn':  'test',
        'userPassword': 'test',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        try:
            inv.add_user(user)
        except ldap.OBJECT_CLASS_VIOLATION:
            return
        else:
            inv.del_user('test')
            raise AssertionError("expected an exception")
