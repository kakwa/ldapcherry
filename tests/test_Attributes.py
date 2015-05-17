#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.attributes import Attributes
from ldapcherry.exceptions import MissingAttributesFile
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError

class TestError(object):

    def testNominal(self):
        inv = Attributes('./tests/cfg/attributes.yml')
        return True

    def testNoFile(self):
        try:
            inv = Attributes('./tests/cfg/dontexist')
        except MissingAttributesFile:
            return
        else:
            raise AssertionError("expected an exception")

#    def testMissingDisplayName(self):
#        try:
#            inv = Attributes('./tests/cfg/attributes_missing_diplay_name.yml')
#        except MissingKey:
#            return
#        else:
#            raise AssertionError("expected an exception")
#
#    def testAttrKeyDuplication(self):
#        try:
#            inv = Attributes('./tests/cfg/attributes_key_dup.yml')
#        except DumplicateAttrKey:
#            return
#        else:
#            raise AssertionError("expected an exception")
#

#    def testGetDisplayNameMissingAttr(self):
#        inv = Attributes('./tests/cfg/attributes.yml')
#        try:
#            res = inv.get_display_name('notarole')
#        except MissingAttr:
#            return
#        else:
#            raise AssertionError("expected an exception")
#
#    def testGetDisplayName(self):
#        inv = Attributes('./tests/cfg/attributes.yml')
#        res = inv.get_display_name('users')
#        expected = 'Simple Users'
#        assert res == expected
#
