# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import os
import sys

from ldapcherry.pyyamlwrapper import loadNoDump
from ldapcherry.pyyamlwrapper import DumplicatedKey
from ldapcherry.exceptions import DumplicateRoleKey, MissingKey, DumplicateRoleContent, MissingRolesFile


class Roles:

    def __init__(self, role_file):
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
