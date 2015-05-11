# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import os
import sys

from ldapcherry.pyyamlwrapper import loadNoDump


class Roles:

    def __init__(self, role_file):
        stream = open(role_file, 'r')
        self.roles_raw = loadNoDump(stream)
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
