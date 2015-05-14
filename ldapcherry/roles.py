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
import yaml

class CustomDumper(yaml.SafeDumper):
    "A custom YAML dumper that never emits aliases"

    def ignore_aliases(self, _data):
        return True

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
        self.roles = {}
        self._nest()

    def _is_parent(self, roleid1, roleid2):
        role2 = self.roles_raw[roleid2]
        role1 = self.roles_raw[roleid1]

        if role1 == role2:
            return False
        # Check if role1 is contained by role2
        for b1 in role1['backends']:
            if not b1 in role2['backends']:
                return False
            for group in role1['backends'][b1]['groups']:
                if not group in role2['backends'][b1]['groups']:
                    return False
        for b2 in role2['backends']:
            if not b2 in role1['backends']:
                return True
            for group in role2['backends'][b2]['groups']:
                if not group in role1['backends'][b2]['groups']:
                    return True
        raise DumplicateRoleContent(roleid1, roleid2)

    def _nest(self):
        """nests the roles (creates roles hierarchy)"""
        parents = {} 
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
                self.backends.add(backend)

            # Create the nested groups
        for roleid in self.roles_raw:
            role = self.roles_raw[roleid]

            parents[roleid]=[]
            for roleid2 in self.roles_raw:
                role2 = self.roles_raw[roleid2]
                if self._is_parent(roleid, roleid2):
                    parents[roleid].append(roleid2)

        for r in parents:
            for p in parents[r]:
                for p2 in parents[r]:
                    if p != p2 and p in parents[p2]:
                        parents[r].remove(p)

        def nest(p):
            ret = self.roles_raw[p]
            ret['subroles'] = {}
            if len(parents[p]) == 0:
                return ret
            else:
                for i in parents[p]: 
                    sub = nest(i)
                    ret['subroles'][i] = sub
                return ret

        for p in parents.keys():
            if p in parents:
                self.roles[p] = nest(p)

    def dump_nest(self):
        """write the nested role hierarchy to a file"""
        return yaml.dump(self.roles, Dumper=CustomDumper)

    def get_roles(self, groups):
        """get list of roles and list of standalone groups"""
        pass

    def get_groups(self, roles):
        """get the list of groups from roles"""
        pass
