#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.attributes import Attributes
from ldapcherry.exceptions import MissingAttributesFile, MissingKey, WrongAttributeType, WrongBackend
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError

class TestError(object):

    def testNominal(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        inv.get_attributes()
        return True

    def testGetSelfAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_selfattributes()
        expected = Set(['password', 'shell'])
        assert ret == expected

    def testGetSelfAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_backends()
        expected = Set(['ldap', 'ad'])
        assert ret == expected

    def testGetBackendAttributes(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        ret = inv.get_backend_attributes('ldap')
        expected = ['shell', 'cn', 'uid', 'uidNumber', 'gidNumber', 'home', 'userPassword', 'givenName', 'email', 'sn']
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

#    def testGetDisplayName(self):
#        inv = Attributes('./tests/cfg/attributes.yml')
#        res = inv.get_display_name('users')
#        expected = 'Simple Users'
#        assert res == expected
