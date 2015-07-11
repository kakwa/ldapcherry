# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

from ldapcherry.exceptions import MissingParameter


class Backend:

    def __init__(self, config, logger, name, attrslist, key):
        raise Exception()

    def auth(self, username, password):
        return False

    def add_user(self, attrs):
        pass

    def del_user(self, username):
        pass

    def set_attrs(self, username, attrs):
        pass

    def add_to_groups(self, username, groups):
        pass

    def del_from_groups(self, username, groups):
        pass

    def search(self, searchstring):
        return {}

    def get_user(self, username):
        return {}

    def get_groups(self, username):
        return []

    def get_param(self, param, default=None):
        if param in self.config:
            return self.config[param]
        elif default is not None:
            return default
        else:
            raise MissingParameter('backends', self.backend_name + '.' + param)
