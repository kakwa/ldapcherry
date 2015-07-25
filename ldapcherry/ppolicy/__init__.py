# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

from ldapcherry.exceptions import MissingParameter


class PPolicy:

    def __init__(self, config, logger):
        """ Password policy constructor

        :param config: the configuration of the ppolicy
        :type config: dict {'config key': 'value'}
        :param logger: the cherrypy error logger object
        :type logger: python logger
        """
        pass

    def check(self, password):
        """ Check if a password match the ppolicy

        :param password: the password to check
        :type password: string
        :rtype: dict with keys 'match' a boolean
            (True if ppolicy matches, False otherwise)
            and 'reason', an explaination string
        """
        ret = {'match': True, 'reason': 'no password policy'}
        return ret

    def info(self):
        """ Give information about the ppolicy

        :rtype: a string describing the ppolicy
        """
        ret = "There is no password policy configured"

    def get_param(self, param, default=None):
        """ Get a parameter in config (handle default value)

        :param param: name of the parameter to recover
        :type param: string
        :param default: the default value, raises an exception
            if param is not in configuration and default
            is None (which is the default value).
        :type default: string or None
        :rtype: the value of the parameter or the default value if
            not set in configuration
        """
        if param in self.config:
            return self.config[param]
        elif default is not None:
            return default
        else:
            raise MissingParameter('ppolicy', param)
