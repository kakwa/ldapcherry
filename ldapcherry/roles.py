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
        self.admin_roles = []
        self._nest()

    def _is_parent(self, roleid1, roleid2):
        """Test if roleid1 is contained inside roleid2"""

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

        # If role2 is inside role1, roles are equal, throw exception
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

            # Create the list of roles which are ldapcherry admins
            if 'LC_admins' in role and role['LC_admins']:
                self.admin_roles.append(roleid)

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
        """dump the nested role hierarchy"""
        return yaml.dump(self.roles, Dumper=CustomDumper)

    def _check_member(self, role, groups, notroles, roles, parentroles, usedgroups):

        # if we have already calculate user is not member of role
        # return False
        if role in notroles:
            return False

        # if we have already calculate that user is already member, skip
        # role membership calculation
        # (parentroles is a list of roles that the user is member of by
        # being member of one of their subroles)
        if not (role in parentroles or role in roles):
            for b in self.roles[role]['backends']:
                for g in self.roles[role]['backends'][b]['groups']:
                    if b not in groups:
                        notroles.add(role)
                        return False
                    if not g in groups[b]:
                        notroles.add(role)
                        return False

        # add groups of the role to usedgroups
        for b in self.roles[role]['backends']:
            if not b in usedgroups:
                usedgroups[b] = Set([])
            for g in self.roles[role]['backends'][b]['groups']:
                usedgroups[b].add(g)

        flag = True
        # recursively determine if user is member of any subrole
        for subrole in self.roles[role]['subroles']:
            flag = flag and not self._check_member(subrole, groups, notroles, roles, parentroles, usedgroups)
        # if not, add role to the list of roles
        if flag:
            roles.add(role)
        # else remove it from the list of roles and add 
        # it to the list of parentroles
        else:
            if role in roles:
                roles.remove(role)
            parentroles.add(role)
        return True

    def get_roles(self, groups):
        """get list of roles and list of standalone groups"""
        roles = Set([])
        parentroles = Set([])
        notroles = Set([])
        usedgroups = {}
        unusedgroups = {}
        ret = {}
        # determine roles membership
        for role in self.roles:
            self._check_member(role, groups, notroles, roles, parentroles, usedgroups)
        # determine standalone groups not matching any roles
        for b in groups:
            for g in groups[b]:
                if not b in usedgroups or not g in usedgroups[b]:
                    if b not in unusedgroups:
                        unusedgroups[b] = Set([])
                    unusedgroups[b].add(g)
        ret['roles'] = roles
        ret['unusedgroups'] = unusedgroups
        return ret

    def get_groups(self, role):
        """get the list of groups from role"""
        return self.roles_raw[role]['backends']

    def is_admin(self, roles):
        """determine from a list of roles if is ldapcherry administrator"""
        for r in roles:
            if r in self.admin_roles:
                return True
        return False

    def get_backends(self):
        """return the list of backends in roles file"""
        return self.backends
