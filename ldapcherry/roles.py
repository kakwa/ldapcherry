# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import os
import sys

from sets import Set
from ldapcherry.pyyamlwrapper import loadNoDump
from ldapcherry.pyyamlwrapper import DumplicatedKey
from ldapcherry.exceptions import DumplicateRoleKey, MissingKey, DumplicateRoleContent, MissingRolesFile


class Roles:

    def __init__(self, role_file):
        self.role_file = role_file
        self.backends = Set([])
        try:
            stream = open(role_file, 'r')
        except:
            raise MissingRolesFile(role_file)
        try:
            self.roles_raw = loadNoDump(stream)
        except DumplicatedKey as e:
            raise DumplicateRoleKey(e.key)
        stream.close()
        self._nest()

    def _nest(self):
        """nests the roles (creates roles hierarchy)"""
        for roleid in self.roles_raw:
            role = self.roles_raw[roleid]

            # Display name is mandatory
            if not 'display_name' in role:
                raise MissingKey('display_name', role, self.role_file)

            # Backend is mandatory
            if not 'backends' in role:
                raise MissingKey('backends', role, self.role_file)

            # Create the list of backends
            for backend in role['backends']:
                self.backends.add(backend['name'])

            # Create the nested groups
            for roleid2 in self.roles_raw:
                role2 = self.roles_raw[roleid2]
        self.roles = self.roles_raw

    def write(self, out_file):
        """write the nested role hierarchy to a file"""
        pass

    def get_roles(self, groups):
        """get list of roles and list of standalone groups"""
        pass

    def get_groups(self, roles):
        """get the list of groups from roles"""
        pass
