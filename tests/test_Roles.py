#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.roles import Roles
from ldapcherry.exceptions import DumplicateRoleKey, MissingKey, DumplicateRoleContent, MissingRolesFile, MissingRole
from ldapcherry.pyyamlwrapper import DumplicatedKey, RelationError

class TestError(object):

    def testNominal(self):
        inv = Roles('./tests/cfg/roles.yml')
        print inv.roles
        return True

    def testMissingDisplayName(self):
        try:
            inv = Roles('./tests/cfg/roles_missing_diplay_name.yml')
        except MissingKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testMissingBackends(self):
        try:
            inv = Roles('./tests/cfg/roles_missing_backends.yml')
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

    def testNoFile(self):
        try:
            inv = Roles('./tests/cfg/dontexist')
        except MissingRolesFile:
            return
        else:
            raise AssertionError("expected an exception")

    def testRoleContentDuplication(self):
        try:
            inv = Roles('./tests/cfg/roles_content_dup.yml')
        except DumplicateRoleContent:
            return
        else:
            raise AssertionError("expected an exception")

    def testGroupsRemove(self):
        inv = Roles('./tests/cfg/roles.yml')
        groups = inv.get_groups_to_remove(
                ['admin-lv2', 'admin-lv3', 'users'],
                ['admin-lv2']
        )
        expected = {'ad': Set(['Administrators', 'Domain Controllers']), 'ldap': Set(['cn=nagios admins,ou=group,dc=example,dc=com', 'cn=puppet admins,ou=group,dc=example,dc=com', 'cn=dns admins,ou=group,dc=example,dc=com'])}
        assert groups == expected

    def testGetGroup(self):
        inv = Roles('./tests/cfg/roles.yml')
        res = inv.get_groups(['users'])
        expected = {
            'ad': ['Domain Users'],
            'ldap': ['cn=users,ou=group,dc=example,dc=com']
        }
        assert res == expected

    def testNested(self):
        inv = Roles('./tests/cfg/nested.yml')
        expected = {'developpers': {'backends_groups': {'ad': ['Domain Users'], 'ldap': ['cn=developpers,ou=group,dc=example,dc=com', 'cn=users,ou=group,dc=example,dc=com']}, 'display_name': 'Developpers', 'description': 'description'}, 'admin-lv3': {'backends_groups': {'ad': ['Domain Users', 'Administrators', 'Domain Controllers'], 'ldap': ['cn=nagios admins,ou=group,dc=example,dc=com', 'cn=users,ou=group,dc=example,dc=com', 'cn=puppet admins,ou=group,dc=example,dc=com', 'cn=dns admins,ou=group,dc=example,dc=com']}, 'display_name': 'Administrators Level 3', 'description': 'description'}, 'admin-lv2': {'backends_groups': {'ad': ['Domain Users'], 'ldap': ['cn=nagios admins,ou=group,dc=example,dc=com', 'cn=users,ou=group,dc=example,dc=com']}, 'display_name': 'Administrators Level 2', 'description': 'description', 'LC_admins': True}, 'users': {'backends_groups': {'ad': ['Domain Users'], 'ldap': ['cn=users,ou=group,dc=example,dc=com']}, 'display_name': 'Simple Users', 'description': 'description'}}
        assert expected == inv.flatten

    def testGetGroupMissingRole(self):
        inv = Roles('./tests/cfg/roles.yml')
        try:
            res = inv.get_groups('notarole')
        except MissingRole:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetDisplayNameMissingRole(self):
        inv = Roles('./tests/cfg/roles.yml')
        try:
            res = inv.get_display_name('notarole')
        except MissingRole:
            return
        else:
            raise AssertionError("expected an exception")

    def testGetDisplayName(self):
        inv = Roles('./tests/cfg/roles.yml')
        res = inv.get_display_name('users')
        expected = 'Simple Users'
        assert res == expected

    def testGetAllRoles(self):
        inv = Roles('./tests/cfg/roles.yml')
        res = inv.get_allroles()
        expected = ['developpers', 'admin-lv3', 'admin-lv2', 'users']
        assert res == expected

    def testGetAllRoles(self):
        inv = Roles('./tests/cfg/roles.yml')
        res = inv.get_backends()
        expected = Set(['ad', 'ldap'])
        assert res == expected

    def testDumpNested(self):
        inv = Roles('./tests/cfg/roles.yml')
        inv.dump_nest()

    def testAdminRoles(self):
        inv = Roles('./tests/cfg/roles.yml')
        res = inv.get_admin_roles()
        expected = ['admin-lv2', 'admin-lv3']
        assert res == expected

    def testIsAdmin(self):
        inv = Roles('./tests/cfg/roles.yml')
        res = inv.is_admin(['admin-lv3', 'users'])
        assert res == True

    def testIsNotAdmin(self):
        inv = Roles('./tests/cfg/roles.yml')
        res = inv.is_admin(['users'])
        assert res == False

    def testGetRole(self):
        inv = Roles('./tests/cfg/roles.yml')
        groups = {
        'ad' : ['Domain Users', 'Domain Users 2'],
        'ldap': ['cn=users,ou=group,dc=example,dc=com',
            'cn=nagios admins,ou=group,dc=example,dc=com',
            'cn=developpers,ou=group,dc=example,dc=com',
            ],
        'toto': ['not a group'],
        }
        expected = {'unusedgroups': {'toto': Set(['not a group']), 'ad': Set(['Domain Users 2'])}, 'roles': Set(['developpers', 'admin-lv2', 'users'])}
        assert inv.get_roles(groups) == expected
