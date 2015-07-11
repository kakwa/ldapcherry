# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import os
import sys
import copy

from sets import Set
from ldapcherry.pyyamlwrapper import loadNoDump
from ldapcherry.pyyamlwrapper import DumplicatedKey
from ldapcherry.exceptions import *
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

        self.graph = {}
        self.roles = {}
        self.flatten = {}
        self.group2roles = {}
        self.admin_roles = []
        self._nest()

    def _merge_groups(self, backends_list):
        """ merge a list backends_groups"""
        ret = {}
        for backends in backends_list:
            for b in backends:
                if b not in ret:
                    ret[b] = Set([])
                for group in backends[b]:
                    ret[b].add(group)
        for b in ret:
            ret[b] = list(ret[b])
        return ret

    def _flatten(self, roles=None, groups=None):
        """ flatten a (semi) nest roles structure"""
        if roles is None:
            roles_in = copy.deepcopy(self.roles_raw)
        else:
            roles_in = roles
        for roleid in roles_in:
            role = roles_in[roleid]
            if groups is not None:
                role['backends_groups'] = self._merge_groups(
                    [role['backends_groups'], groups],
                    )
            if 'subroles' in role:
                self._flatten(
                    role['subroles'],
                    role['backends_groups'],
                    )
                del role['subroles']

            self.flatten[roleid] = role

    def _set_admin(self, role):
        for r in role['subroles']:
            self.admin_roles.append(r)
            self._set_admin(role['subroles'][r])

    def _is_parent(self, roleid1, roleid2):
        """Test if roleid1 is contained inside roleid2"""

        role2 = copy.deepcopy(self.flatten[roleid2])
        role1 = copy.deepcopy(self.flatten[roleid1])

        if role1 == role2:
            return False

        # Check if role1 is contained by role2
        for b1 in role1['backends_groups']:
            if b1 not in role2['backends_groups']:
                return False
            for group in role1['backends_groups'][b1]:
                if group not in role2['backends_groups'][b1]:
                    return False

        # If role2 is inside role1, roles are equal, throw exception
        for b2 in role2['backends_groups']:
            if b2 not in role1['backends_groups']:
                return True
            for group in role2['backends_groups'][b2]:
                if group not in role1['backends_groups'][b2]:
                    return True
        raise DumplicateRoleContent(roleid1, roleid2)

    def _nest(self):
        """nests the roles (creates roles hierarchy)"""
        self._flatten()
        parent_roles = {}
        for roleid in self.flatten:
            role = copy.deepcopy(self.flatten[roleid])

            # Display name is mandatory
            if 'display_name' not in role:
                raise MissingKey('display_name', role, self.role_file)

            if 'description' not in role:
                raise MissingKey('description', role, self.role_file)

            # Backend is mandatory
            if 'backends_groups' not in role:
                raise MissingKey('backends_groups', role, self.role_file)

            # Create the list of backends
            for backend in role['backends_groups']:
                self.backends.add(backend)

            if roleid not in self.graph:
                self.graph[roleid] = {
                    'parent_roles': Set([]),
                    'sub_roles': Set([])
                    }

        # Create the nested groups
        for roleid in self.flatten:
            role = copy.deepcopy(self.flatten[roleid])
            # create reverse groups 2 roles
            for b in role['backends_groups']:
                for g in role['backends_groups'][b]:
                    if b not in self.group2roles:
                        self.group2roles[b] = {}
                    if g not in self.group2roles[b]:
                        self.group2roles[b][g] = Set([])
                    self.group2roles[b][g].add(roleid)

            parent_roles[roleid] = []
            for roleid2 in self.flatten:
                role2 = copy.deepcopy(self.flatten[roleid2])
                if self._is_parent(roleid, roleid2):
                    parent_roles[roleid].append(roleid2)
                    self.graph[roleid2]['parent_roles'].add(roleid)
                    self.graph[roleid]['sub_roles'].add(roleid2)

        for r in parent_roles:
            for p in parent_roles[r]:
                for p2 in parent_roles[r]:
                    if p != p2 and p in parent_roles[p2]:
                        parent_roles[r].remove(p)

        def nest(p):
            ret = copy.deepcopy(self.flatten[p])
            ret['subroles'] = {}
            if len(parent_roles[p]) == 0:
                return ret
            else:
                for i in parent_roles[p]:
                    sub = nest(i)
                    ret['subroles'][i] = sub
                return ret

        for p in parent_roles.keys():
            if p in parent_roles:
                self.roles[p] = nest(p)

        for roleid in self.roles:
            role = self.roles[roleid]
            # Create the list of roles which are ldapcherry admins
            if 'LC_admins' in role and role['LC_admins']:
                self.admin_roles.append(roleid)
                self._set_admin(role)

    def get_admin_roles(self):
        return self.admin_roles

    def dump_nest(self):
        """dump the nested role hierarchy"""
        return yaml.dump(self.roles, Dumper=CustomDumper)

    def dump_flatten(self):
        """dump the nested role hierarchy"""
        return yaml.dump(self.flatten, Dumper=CustomDumper)

    def _check_member(
            self, role, groups, notroles,
            roles, parentroles, usedgroups):

        # if we have already calculate user is not member of role
        # return False
        if role in notroles:
            return False

        # if we have already calculate that user is already member, skip
        # role membership calculation
        # (parentroles is a list of roles that the user is member of by
        # being member of one of their subroles)
        if not (role in parentroles or role in roles):
            for b in self.roles[role]['backends_groups']:
                for g in self.roles[role]['backends_groups'][b]:
                    if b not in groups:
                        notroles.add(role)
                        return False
                    if g not in groups[b]:
                        notroles.add(role)
                        return False

        # add groups of the role to usedgroups
        for b in self.roles[role]['backends_groups']:
            if b not in usedgroups:
                usedgroups[b] = Set([])
            for g in self.roles[role]['backends_groups'][b]:
                usedgroups[b].add(g)

        flag = True
        # recursively determine if user is member of any subrole
        for subrole in self.roles[role]['subroles']:
            flag = flag and not \
                self._check_member(
                    subrole,
                    groups,
                    notroles,
                    roles,
                    parentroles,
                    usedgroups,
                    )
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

    def get_groups_to_remove(self, current_roles, roles_to_remove):
        """get groups to remove from list of
        roles to remove and current roles
        """
        current_roles = Set(current_roles)

        ret = {}
        roles_to_remove = Set(roles_to_remove)
        tmp = Set([])
        # get sub roles of the role to remove that the user belongs to
        # if we remove a role, there is no reason to keep the sub roles
        for r in roles_to_remove:
            for sr in self._get_subroles(r):
                if sr not in roles_to_remove and sr in current_roles:
                    tmp.add(sr)

        roles_to_remove = roles_to_remove.union(tmp)
        roles = current_roles.difference(Set(roles_to_remove))
        groups_roles = self._get_groups(roles)
        groups_roles_to_remove = self._get_groups(roles_to_remove)

        # if groups belongs to roles the user keeps, don't remove it
        for b in groups_roles_to_remove:
            if b in groups_roles:
                groups_roles_to_remove[b] = \
                    groups_roles_to_remove[b].difference(groups_roles[b])
        return groups_roles_to_remove

    def _get_groups(self, roles):
        ret = {}
        for r in roles:
            for b in self.flatten[r]['backends_groups']:
                groups = self.flatten[r]['backends_groups'][b]
                if b not in ret:
                    ret[b] = Set(groups)
                ret[b] = ret[b].union(Set(groups))
        return ret

    def _get_subroles(self, role):
        ret = Set([])
        for sr in self.graph[role]['sub_roles']:
            tmp = self._get_subroles(sr)
            tmp.add(sr)
            ret = ret.union(tmp)
        return ret

    def get_roles(self, groups):
        """get list of roles and list of standalone groups"""
        roles = Set([])
        parentroles = Set([])
        notroles = Set([])
        tmp = Set([])
        usedgroups = {}
        unusedgroups = {}
        ret = {}
        # determine roles membership
        for role in self.roles:
            if self._check_member(
                    role, groups, notroles,
                    tmp, parentroles, usedgroups):
                roles.add(role)
        # determine standalone groups not matching any roles
        for b in groups:
            for g in groups[b]:
                if b not in usedgroups or g not in usedgroups[b]:
                    if b not in unusedgroups:
                        unusedgroups[b] = Set([])
                    unusedgroups[b].add(g)

        ret['roles'] = roles
        ret['unusedgroups'] = unusedgroups
        return ret

    def get_allroles(self):
        """get the list of roles"""
        return self.flatten.keys()

    def get_display_name(self, role):
        """get the display name of a role"""
        if role not in self.flatten:
            raise MissingRole(role)
        return self.flatten[role]['display_name']

    def get_groups(self, roles):
        """get the list of groups from role"""
        ret = {}
        for role in roles:
            if role not in self.flatten:
                raise MissingRole(role)
            for b in self.flatten[role]['backends_groups']:
                if b not in ret:
                    ret[b] = []
                ret[b] = ret[b] + self.flatten[role]['backends_groups'][b]
        return ret

    def is_admin(self, roles):
        """determine from a list of roles if is ldapcherry administrator"""
        for r in roles:
            if r in self.admin_roles:
                return True
        return False

    def get_backends(self):
        """return the list of backends in roles file"""
        return self.backends
