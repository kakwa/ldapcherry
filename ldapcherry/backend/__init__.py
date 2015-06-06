# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

from ldapcherry.exceptions import MissingParameter

class Backend:

    def __init__(self):
        pass

    def auth(self, username, password):
        return False

    def add_user(self, attrs):
        pass

    def del_user(self, username):
        pass

    def set_attrs(self, attrs, username):
        pass

    def add_to_group(self, username):
        pass

    def rm_from_group(self, username):
        pass

    def search(self, searchstring):
        return []

    def get_user(self, username):
        return None

    def get_groups(self, username):
        return []

    def get_param(self, param, default=None):
        if param in self.config:
            return self.config[param]
        elif not default is None:
            return default
        else:
            raise MissingParameter('backends', self.backend_name+'.'+param)

