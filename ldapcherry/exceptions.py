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
