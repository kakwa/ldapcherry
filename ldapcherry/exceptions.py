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
        self.log = "missing parameter <%(key)s> in section <%(section)s>" % { 'key' : key, 'section' : section }

class MissingKey(Exception):
    def __init__(self, key):
        self.key = key

class DumplicateRoleKey(Exception):
    def __init__(self, role):
        self.role = role
        self.log = "duplicate role key <%(role)s> in role file" % { 'role' : role}

class DumplicateRoleContent(Exception):
    def __init__(self, role1, role2):
        self.role1 = role1
        self.role2 = role2
        self.log = "role <%(role1)s> and <%(role2)s> are identical" % { 'role1' : role1, 'role2': role2}

class MissingRolesFile(Exception):
    def __init__(self, rolefile):
        self.rolefile = rolefile
        self.log = "fail to open role file <%(rolefile)s>" % { 'rolefile' : rolefile}


