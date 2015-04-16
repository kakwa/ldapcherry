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

class Attributes:

    def __init__(self, attributes_file):
        pass

    def get_selfattributes(self):
        """get the list of groups from roles"""
        pass

    def get_addattributes(self):
        """get the list of groups from roles"""
        pass
