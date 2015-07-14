# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

from ldapcherry.exceptions import MissingParameter


class PPolicy:

    def __init__(self, config, logger):
        """ password policy constructor
        @dict config: the configuration of the ppolicy
        @logger logger: a python logger
        """
        pass

    def check(self, password):
        """ check that a password match the ppolicy
        @str password: the password to check
        @rtype: dict with keys 'match' a boolean
            (True if ppolicy matches, False otherwise)
            and 'reason', an explaination string
        """
        ret = {'match': True, 'reason': 'no password policy'}
        return ret

    def info(self):
        """ gives information about the ppolicy
        @rtype: a string describing the ppolicy
        """
        ret = "There is no password policy configured"

    def get_param(self, param, default=None):
        """
        @str param: name of the paramter to recover
        default: the default value, raises an exception
            if param is not in configuration and default
            is None (which is the default value).
        """
        if param in self.config:
            return self.config[param]
        elif default is not None:
            return default
        else:
            raise MissingParameter('ppolicy', param)
