# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

class MissingParameter(Exception):
    def __init__(self, section, key):
        self.section = section
        self.key = key

class MissingKey(Exception):
    def __init__(self, key):
        self.key = key

class DumplicateRoleKey(Exception):
    def __init__(self, role):
        self.role = role

class DumplicateRoleContent(Exception):
    def __init__(self, role1, role2):
        self.role1 = role1
        self.role2 = role2
