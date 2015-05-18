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
    def __init__(self, key, section, ymlfile):
        self.key = key
        self.section = section
        self.ymlfile = ymlfile
        self.log = "missing key <%(key)s> in section <%(section)s> inside file <%(ymlfile)s>" % {'key': key, 'section': section, 'ymlfile': ymlfile } 

class DumplicateRoleKey(Exception):
    def __init__(self, role):
        self.role = role
        self.log = "duplicate role key <%(role)s> in role file" % { 'role' : role}

class MissingRole(Exception):
    def __init__(self, role):
        self.role = role
        self.log = "role <%(role)s> does not exist in role file" % { 'role' : role}

class DumplicateRoleContent(Exception):
    def __init__(self, role1, role2):
        self.role1 = role1
        self.role2 = role2
        self.log = "role <%(role1)s> and <%(role2)s> are identical" % { 'role1' : role1, 'role2': role2}

class MissingRolesFile(Exception):
    def __init__(self, rolefile):
        self.rolefile = rolefile
        self.log = "fail to open role file <%(rolefile)s>" % { 'rolefile' : rolefile}

class MissingMainFile(Exception):
    def __init__(self, config):
        self.rolefile = rolefile
        self.log = "fail to open main file <%(config)s>" % { 'rolefile' : rolefile}



class MissingAttributesFile(Exception):
    def __init__(self, attributesfile):
        self.attributesfile = attributesfile
        self.log = "fail to open attributes file <%(attributesfile)s>" % { 'attributesfile' : attributesfile}

class WrongAttributeType(Exception):
    def __init__(self, key, section, ymlfile):
        self.key = key
        self.section = section
        self.ymlfile = ymlfile
        self.log = "wrong attribute type <%(key)s> in section <%(section)s> inside file <%(ymlfile)s>" % {'key': key, 'section': section, 'ymlfile': ymlfile } 


