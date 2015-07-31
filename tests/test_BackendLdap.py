#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.backend.backendLdap import Backend, CaFileDontExist
from ldapcherry.exceptions import *
from disable import travis_disabled
import cherrypy
import logging
import ldap

cfg = {
'module'             : 'ldapcherry.backend.ldap',
'groupdn'            : 'ou=groups,dc=example,dc=org',
'userdn'             : 'ou=People,dc=example,dc=org',
'binddn'             : 'cn=dnscherry,dc=example,dc=org',
'password'           : 'password',
'uri'                : 'ldap://ldap.dnscherry.org:390',
'ca'                 : './tests/test_env/etc/ldapcherry/TEST-cacert.pem',
'starttls'           : 'off',
'checkcert'          : 'off',
'user_filter_tmpl'   : '(uid=%(username)s)',
'group_filter_tmpl'  : '(member=%(userdn)s)',
'search_filter_tmpl' : '(|(uid=%(searchstring)s*)(sn=%(searchstring)s*))',
'objectclasses'      : 'top, person, organizationalPerson, simpleSecurityObject, posixAccount',
'dn_user_attr'       : 'uid',
'group_attr.member'  : "%(dn)s",
'timeout'            : 10,
'display_name'       : 'My Test Ldap',
}

def syslog_error(msg='', context='',
        severity=logging.INFO, traceback=False):
    pass

cherrypy.log.error = syslog_error
attr = ['shéll', 'shell', 'cn', 'uid', 'uidNumber', 'gidNumber', 'home', 'userPassword', 'givenName', 'email', 'sn']

class TestError(object):

    def testNominal(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        return True

    def testConnectSSLNoCheck(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
        cfg2['checkcert'] = 'off'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr, 'uid')
        ldap = inv._connect()
        ldap.simple_bind_s(inv.binddn, inv.bindpassword)

    def testConnect(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        ldap = inv._connect()
        ldap.simple_bind_s(inv.binddn, inv.bindpassword)
        return True

    def testConnectSSL(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.dnscherry.org:637'
        cfg2['checkcert'] = 'on'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr, 'uid')
        ldap = inv._connect()
        ldap.simple_bind_s(inv.binddn, inv.bindpassword)

    def testLdapUnavaible(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://notaldap:637'
        cfg2['checkcert'] = 'on'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr, 'uid')
        try:
            ldapc = inv._connect()
            ldapc.simple_bind_s(inv.binddn, inv.bindpassword)
        except ldap.SERVER_DOWN as e:
            return
        else:
            raise AssertionError("expected an exception")

    def testMissingCA(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.dnscherry.org:637'
        cfg2['checkcert'] = 'on'
        cfg2['ca'] = './test/cfg/not_a_ca.crt'
        try:
            inv = Backend(cfg2, cherrypy.log, 'ldap', attr, 'uid')
            ldapc = inv._connect()
        except CaFileDontExist as e:
            return
        else:
            raise AssertionError("expected an exception")

    def testConnectSSLWrongCA(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldaps://ldap.ldapcherry.org:637'
        cfg2['checkcert'] = 'on'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr, 'uid')
        ldapc = inv._connect()
        try:
            ldapc.simple_bind_s(inv.binddn, inv.bindpassword)
        except ldap.SERVER_DOWN as e:
            assert e[0]['info'] == 'TLS: hostname does not match CN in peer certificate'
        else:
            raise AssertionError("expected an exception")

    def testConnectStartTLS(self):
        cfg2 = cfg.copy()
        cfg2['uri'] = 'ldap://ldap.ldapcherry.org:390'
        cfg2['checkcert'] = 'off'
        cfg2['starttls'] = 'on'
        cfg2['ca'] = './test/cfg/ca.crt'
        inv = Backend(cfg2, cherrypy.log, 'ldap', attr, 'uid')
        ldapc = inv._connect()
        ldapc.simple_bind_s(inv.binddn, inv.bindpassword)

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        ret = inv.auth('jwatson', 'passwordwatson')
        assert ret == True

    def testAuthFailure(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        res = inv.auth('notauser', 'password') or inv.auth('jwatson', 'notapassword')
        assert res == False

    def testMissingParam(self):
        cfg2 = {}
        return True
        try:
            inv = Backend(cfg2, cherrypy.log, 'ldap', attr, 'uid')
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        ret = inv.get_user('jwatson')
        expected = {'uid': 'jwatson', 'cn': 'John Watson', 'sn': 'watson'}
        assert ret == expected

    def testGetGroups(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        ret = inv.get_groups('jwatson')
        expected = ['cn=itpeople,ou=Groups,dc=example,dc=org']
        assert ret == expected

    def testAddDeleteGroups(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        groups = [
           'cn=hrpeople,ou=Groups,dc=example,dc=org',
           'cn=itpeople,ou=Groups,dc=example,dc=org',
        ]
        inv.add_to_groups('jwatson', groups)
        ret = inv.get_groups('jwatson')
        print ret
        inv.del_from_groups('jwatson', ['cn=hrpeople,ou=Groups,dc=example,dc=org'])
        inv.del_from_groups('jwatson', ['cn=hrpeople,ou=Groups,dc=example,dc=org'])
        assert ret == ['cn=itpeople,ou=Groups,dc=example,dc=org', 'cn=hrpeople,ou=Groups,dc=example,dc=org']


    def testSearchUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        ret = inv.search('smith')
        expected = {'ssmith': {'sn': 'smith', 'uid': 'ssmith', 'cn': 'Sheri Smith', 'userPassword': 'passwordsmith'}, 'jsmith': {'sn': 'Smith', 'uid': 'jsmith', 'cn': 'John Smith', 'userPassword': 'passwordsmith'}}
        assert ret == expected

    def testAddUser(self):
        try:
            inv.del_user(u'test☭')
        except:
            pass
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        user = {
        'uid': u'test☭',
        'sn':  'test',
        'cn':  'test',
        'userPassword': 'test',
        'uidNumber': '42',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        inv.add_user(user)
        inv.del_user(u'test☭')

    def testModifyUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        user = {
        'uid': u'test☭',
        'sn':  'test',
        'cn':  'test',
        'userPassword': 'test',
        'uidNumber': '42',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        inv.add_user(user)
        inv.set_attrs(u'test☭', {'gecos': 'test2', 'homeDirectory': '/home/test/'})
        inv.del_user(u'test☭')

    def testAddUserDuplicate(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
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
        except UserAlreadyExists:
            inv.del_user('test')
            return
        else:
            inv.del_user('test')
            raise AssertionError("expected an exception")

    def testDelUserDontExists(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        try:
            inv.del_user('test')
            inv.del_user('test')
        except UserDoesntExist:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
        ret = inv.get_user('jwatson')
        expected = {'uid': 'jwatson', 'objectClass': 'inetOrgPerson', 'carLicense': 'HERCAR 125', 'sn': 'watson', 'mail': 'j.watson@example.com', 'homePhone': '555-111-2225', 'cn': 'John Watson', 'userPassword': u'passwordwatson'}
        assert ret == expected

    def testAddUserMissingMustattribute(self):
        inv = Backend(cfg, cherrypy.log, 'ldap', attr, 'uid')
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
