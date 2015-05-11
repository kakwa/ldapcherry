#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from ldapcherry.roles import Roles
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError


class TestError(object):

    def testNominal(self):
        inv = Roles('./tests/cfg/roles.yml')
        print inv.roles
        return True

    def testMissingDisplayName(self):
        try:
            inv = Roles('./cfg/roles_missing_diplay_name.yml')
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testRoleKeyDuplication(self):
        try:
            inv = Roles('./tests/cfg/roles_key_dup.yml')
        except DumplicateRoleKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testRoleContentDuplication(self):
        try:
            inv = Roles('./tests/cfg/roles_content_dump.yml')
        except DumplicateRoleContent:
            return
        else:
            raise AssertionError("expected an exception")

