#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.backend.backendAD import Backend
from ldapcherry.exceptions import *
from disable import travis_disabled
import cherrypy
import logging

cfg = {
    'display_name': u'test☭',
    'domain': 'DC.LDAPCHERRY.ORG',
    'login': 'Administrator',
    'password': 'qwertyP455',
    'uri': 'ldaps://ad.ldapcherry.org',
    'checkcert': 'off',
}

def syslog_error(msg='', context='',
        severity=logging.INFO, traceback=False):
    pass

cherrypy.log.error = syslog_error
attr = ['shell', 'cn', 'sAMAccountName', 'uidNumber', 'gidNumber', 'home', 'unicodePwd', 'givenName', 'email', 'sn']

default_user = {
'sAMAccountName': u'☭default_user',
'sn':  u'test☭1',
'cn':  u'test☭2',
'unicodePwd': u'test☭P666',
'uidNumber': '42',
'gidNumber': '42',
'homeDirectory': '/home/test/'
}

default_user2 = {
'sAMAccountName': u'☭default_user2',
'sn':  u'test☭ 2',
'cn':  u'test☭ 2',
'unicodePwd': u'test☭P666',
'uidNumber': '42',
'gidNumber': '42',
'homeDirectory': '/home/test/'
}



default_groups = ['Domain Admins', 'Backup Operators']


class TestError(object):

    @travis_disabled
    def testNominal(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        return True

    @travis_disabled
    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        ret = inv.auth('Administrator', 'qwertyP455')
        assert ret == True

    @travis_disabled
    def testAuthFailure(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        res = inv.auth('notauser', 'password') or inv.auth(u'☭default_user', 'notapassword')
        assert res == False

    @travis_disabled
    def testMissingParam(self):
        cfg2 = {}
        return True
        try:
            inv = Backend(cfg2, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    @travis_disabled
    def testSetPassword(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        try:
            inv.add_user(default_user.copy())
            inv.add_to_groups(u'☭default_user', default_groups)
        except:
            pass
	inv.set_attrs(u'☭default_user', {'unicodePwd': u'test☭P66642$'})
        ret = inv.auth(u'☭default_user', u'test☭P66642$')
        inv.del_user(u'☭default_user')
        assert ret == True

    @travis_disabled
    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        try:
            inv.add_user(default_user.copy())
            inv.add_to_groups(u'☭default_user', default_groups)
        except:
            pass
        ret = inv.get_user(u'☭default_user')
        expected = default_user 
        inv.del_user(u'☭default_user')
        for i in default_user:
            if i != 'unicodePwd':
                assert ret[i] == expected[i]

    @travis_disabled
    def testGetGroups(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        try:
            inv.add_user(default_user.copy())
            inv.add_to_groups(u'☭default_user', default_groups)
        except:
            pass
        ret = inv.get_groups(u'☭default_user')
        expected = ['Domain Admins', 'Backup Operators']
        inv.del_user(u'☭default_user')
        assert ret == expected

    @travis_disabled
    def testSearchUser(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        try:
            inv.add_user(default_user.copy())
        except:
            pass
        inv.add_user(default_user2.copy())
        ret = inv.search(u'test☭')
        expected = [u'☭default_user', u'☭default_user2']
        inv.del_user(u'☭default_user')
        inv.del_user(u'☭default_user2')
        assert Set(ret.keys()) == Set(expected)

    @travis_disabled
    def testAddUser(self):
        try:
            inv.del_user(u'test☭')
        except:
            pass
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        user = {
        'sAMAccountName': u'test☭',
        'sn':  u'test☭',
        'cn':  u'test☭',
        'unicodePwd': u'test☭0918M',
        'uidNumber': '42',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        inv.add_user(user)
        inv.del_user(u'test☭')

    @travis_disabled
    def testModifyUser(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        user = {
        'sAMAccountName': u'test☭',
        'sn':  u'test☭',
        'cn':  u'test☭',
        'unicodePwd': u'test☭Aowo87',
        'uidNumber': '42',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        inv.add_user(user)
        inv.set_attrs(u'test☭', {'gecos': 'test2', 'homeDirectory': '/home/test/'})
        inv.del_user(u'test☭')

    @travis_disabled
    def testAddUserDuplicate(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        user = {
        'sAMAccountName': u'test☭',
        'sn':  u'test☭',
        'cn':  u'test☭',
        'uidNumber': '42',
        'unicodePwd': u'test☭aqosJK87',
        'gidNumber': '42',
        'homeDirectory': '/home/test/'
        }
        try:
            inv.add_user(user.copy())
            inv.add_user(user.copy())
        except UserAlreadyExists:
            inv.del_user(u'test☭')
            return
        else:
            inv.del_user(u'test☭')
            raise AssertionError("expected an exception")

    @travis_disabled
    def testDelUserDontExists(self):
        inv = Backend(cfg, cherrypy.log, u'test☭', attr, 'sAMAccountName')
        try:
            inv.del_user(u'test☭')
            inv.del_user(u'test☭')
        except UserDoesntExist:
            return
        else:
            raise AssertionError("expected an exception")
