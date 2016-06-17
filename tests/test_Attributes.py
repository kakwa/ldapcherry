#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.attributes import Attributes
from ldapcherry.exceptions import *
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError

class TestError(object):

    def testNominal(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        inv.get_attributes()
        return True

    def testGetSelfAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_selfattributes()
        expected = {'password': {'backends': {'ad': 'unicodePwd', 'ldap': 'userPassword'}, 'display_name': 'Password', 'description': 'Password of the user', 'weight': 31, 'self': True, 'type': 'password'}, 'shell': {'backends': {'ad': 'SHELL', 'ldap': 'shell'}, 'display_name': 'Shell', 'description': 'Shell of the user', 'weight': 80, 'values': ['/bin/bash', '/bin/zsh', '/bin/sh'], 'self': True, 'type': 'stringlist'}}
        assert ret == expected

    def testGetSelfAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_backends()
        expected = Set(['ldap', 'ad'])
        assert ret == expected

    def testGetSearchAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_search_attributes()
        expected = {'first-name': {'backends': {'ad': 'givenName', 'ldap': 'givenName'}, 'display_name': 'First Name', 'description': 'First name of the user', 'weight': 20, 'search_displayed': True, 'type': 'string'}, 'cn': {'autofill': {'function': 'cn', 'args': ['$first-name', '$name']}, 'backends': {'ad': 'cn', 'ldap': 'cn'}, 'display_name': 'Display Name', 'description': 'Firt Name and Display Name', 'weight': 30, 'search_displayed': True, 'type': 'string'}, 'name': {'backends': {'ad': 'sn', 'ldap': 'sn'}, 'display_name': 'Name', 'description': 'Family name of the user', 'weight': 10, 'search_displayed': True, 'type': 'string'}, 'uid': {'display_name': 'UID', 'description': 'UID of the user', 'weight': 50, 'autofill': {'function': 'uid', 'args': ['$first-name', '$last-name']}, 'backends': {'ad': 'UID', 'ldap': 'uid'}, 'key': True, 'search_displayed': True, 'type': 'string'}}
        assert ret == expected

    def testGetBackendAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_backend_attributes('ldap')
        expected = ['shell', 'cn', 'userPassword', 'uidNumber', 'gidNumber', 'sn', 'home', 'givenName', 'email', 'uid']
        assert ret == expected

    def testGetKey(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_key()
        expected = 'uid'
        assert ret == expected

    def testWrongGetBackendAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        try:
            ret = inv.get_backend_attributes('notabackend')
        except WrongBackend:
            return
        else:
            raise AssertionError("expected an exception")

    def testNoFile(self):
        try:
            inv = Attributes('./tests/cfg/dontexist')
        except MissingAttributesFile:
            return
        else:
            raise AssertionError("expected an exception")

    def testMissingMandatory(self):
        try:
            inv = Attributes('./tests/cfg/attributes_missing_mandatory.yml')
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testWrongType(self):
        try:
            inv = Attributes('./tests/cfg/attributes_wrong_type.yml')
        except WrongAttributeType:
            return
        else:
            raise AssertionError("expected an exception")

    def testDuplicatePassword(self):
        try:
            inv = Attributes('./tests/cfg/attribute_pwderror.yml')
        except PasswordAttributesCollision:
            return
        else:
            raise AssertionError("expected an exception")

    def testValidate(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        attrs = {'cn': 'test', 'email': 'test@example.org', 'uidNumber': 4242, 'shell': '/bin/bash', 'logscript': 'login1.bat'}
        for attrid in attrs:
            inv.check_attr(attrid, attrs[attrid])

    def testValidateError(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        attrs = {'email': 'notamail', 'uidNumber': 'not an integer', 'shell': '/bin/not in list', 'logscript': 'not fixed'}
        for attrid in attrs:
            try:
                inv.check_attr(attrid, attrs[attrid])
            except WrongAttrValue:
                pass
            else:
                raise AssertionError("expected an exception")

#    def testGetDisplayName(self):
#        inv = Attributes('./tests/cfg/attributes.yml')
#        res = inv.get_display_name('users')
#        expected = 'Simple Users'
#        assert res == expected
