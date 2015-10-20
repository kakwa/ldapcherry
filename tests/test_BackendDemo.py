#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.backend.backendDemo import Backend
from ldapcherry.exceptions import *
from disable import travis_disabled
import cherrypy
import logging

cfg = {
    'display_name': 'test',
    'admin.groups': 'grp1, grp2',
    'basic.groups': 'grp1, grp2, grp3',
    'pwd_attr': 'userPassword',
    'search_attributes': 'uid',
}

def syslog_error(msg='', context='',
        severity=logging.INFO, traceback=False):
    pass

cherrypy.log.error = syslog_error
attr = ['shéll', 'shell', 'cn', 'uid', 'uidNumber', 'gidNumber', 'home', 'userPassword', 'givenName', 'email', 'sn']

default_user = {
'uid': 'default_user',
'sn':  'test',
'cn':  'test',
'userPassword': 'test',
'uidNumber': '42',
'gidNumber': '42',
'homeDirectory': '/home/test/'
}

default_user2 = {
'uid': 'default_user2',
'sn':  'test',
'cn':  'test',
'userPassword': 'test',
'uidNumber': '42',
'gidNumber': '42',
'homeDirectory': '/home/test/'
}



default_groups = ['grp1', 'grp2', 'grp3']


class TestError(object):

    def testNominal(self):
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
        return True

    def testAuthSuccess(self):
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
        ret = inv.auth('admin', 'admin')
        assert ret == True

    def testAuthFailure(self):
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
        res = inv.auth('notauser', 'password') or inv.auth('default_user', 'notapassword')
        assert res == False

    def testMissingParam(self):
        cfg2 = {}
        return True
        try:
            inv = Backend(cfg2, cherrypy.log, 'test', attr, 'uid')
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetUser(self):
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
        inv.add_user(default_user)
        inv.add_to_groups('default_user', default_groups)
        ret = inv.get_user('default_user')
        expected = default_user 
        assert ret == expected

    def testGetGroups(self):
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
        inv.add_user(default_user)
        inv.add_to_groups('default_user', default_groups)
        ret = inv.get_groups('default_user')
        expected = Set(default_groups)
        assert ret == expected

    def testSearchUser(self):
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
        inv.add_user(default_user)
        inv.add_user(default_user2)
        ret = inv.search('default')
        expected = ['default_user', 'default_user2']
        assert Set(ret.keys()) == Set(expected)

    def testAddUser(self):
        try:
            inv.del_user(u'test☭')
        except:
            pass
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
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
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
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
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
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
        inv = Backend(cfg, cherrypy.log, 'test', attr, 'uid')
        try:
            inv.del_user('test')
            inv.del_user('test')
        except UserDoesntExist:
            return
        else:
            raise AssertionError("expected an exception")
