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
from ldapcherry.exceptions import MissingAttributesFile, MissingKey, WrongAttributeType, WrongBackend, DumplicateUserKey, MissingUserKey
from sets import Set
import yaml

types = ['string', 'email', 'int', 'stringlist', 'fix', 'password']

class Attributes:

    def __init__(self, attributes_file):
        self.attributes_file = attributes_file
        self.backends = Set([])
        self.self_attributes = {}
        self.backend_attributes = {}
        self.displayed_attributes = {}
        self.key = None
        try:
            stream = open(attributes_file, 'r')
        except:
            raise MissingAttributesFile(attributes_file)
        try:
            self.attributes = loadNoDump(stream)
        except DumplicatedKey as e:
            raise DumplicateAttributesKey(e.key)

        for attrid in self.attributes:
            self._mandatory_check(attrid)
            attr = self.attributes[attrid]
            if not attr['type'] in types:
                raise WrongAttributeType(attr['type'], attrid, attributes_file)
            if 'self' in attr and attr['self']:
                self.self_attributes[attrid] = attr
            if 'key' in attr and attr['key']:
                if not self.key is None:
                    raise DumplicateUserKey(attrid, self.key)
                self.key = attrid
            for b in attr['backends']:
                self.backends.add(b)
                if b not in self.backend_attributes:
                    self.backend_attributes[b] = {}
                self.backend_attributes[b][attr['backends'][b]] = attrid
            if 'search_displayed' in attr and attr['search_displayed']:
                self.displayed_attributes[attrid] = attr

        if self.key is None:
            raise MissingUserKey()

    def get_search_attributes(self):
        return self.displayed_attributes

    def get_key(self):
        return self.key

    def _mandatory_check(self, attr):
        for m in ['description', 'display_name', 'type', 'backends', 'weight']:
            if m not in self.attributes[attr]:
                raise MissingKey(m, attr, self.attributes_file)

    def get_selfattributes(self):
        """get the list of groups from roles"""
        return self.self_attributes

    def get_backends(self):
        """return the list of backends in roles file"""
        return self.backends

    def get_backend_attributes(self, backend):
        if backend not in self.backends:
            raise WrongBackend(backend)
        return self.backend_attributes[backend].keys()

    def get_backend_key(self, backend):
        if backend not in self.backends:
            raise WrongBackend(backend)
        return self.attributes[self.key]['backends'][backend]

    def get_attributes(self):
        """get the list of groups from roles"""
        return self.attributes.keys()

    def get_backends_attributes(self, attribute):
        return self.attributes[attribute]['backends']
