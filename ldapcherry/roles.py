# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import os
import sys

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Roles:

    def __init__(self, role_file):
        pass

    def _nest(self, role_file):
        """nests the roles (creates roles hierarchy)"""
        pass

    def write(self, out_file):
        """write the nested role hierarchy to a file"""
        pass

    def get_roles(self, groups):
        """get list of roles and list of standalone groups"""
        pass

    def get_groups(self, roles):
        """get the list of groups from roles"""
        pass
