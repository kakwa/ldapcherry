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
from ldapcherry.exceptions import MissingAttributesFile
from sets import Set
import yaml

types = ['string', 'email', 'int', 'stringlist', 'fix', 'password']

class Attributes:

    def __init__(self, attributes_file):
        self.attributes_file = attributes_file
        self.backends = Set([])
        try:
            stream = open(attributes_file, 'r')
        except:
            raise MissingAttributesFile(attributes_file)
        try:
            self.attributes = loadNoDump(stream)
        except DumplicatedKey as e:
            raise DumplicateAttributesKey(e.key)

    def get_selfattributes(self):
        """get the list of groups from roles"""
        pass

    def get_addattributes(self):
        """get the list of groups from roles"""
        pass
