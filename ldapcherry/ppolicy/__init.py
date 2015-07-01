# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

class Ppolicy:

    def __init__(self, config, logger):
        pass

    def check(self, password):
        ret = {'match': True, 'reason': 'no password policy'}

    def info(self):
        ret = "There is no password policy configured"
