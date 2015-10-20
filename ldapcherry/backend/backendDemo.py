# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

# This is a demo backend

from sets import Set
import ldapcherry.backend
from ldapcherry.exceptions import UserDoesntExist, \
    GroupDoesntExist, MissingParameter, \
    UserAlreadyExists
import re


class Backend(ldapcherry.backend.Backend):

    def __init__(self, config, logger, name, attrslist, key):
        """ Initialize the backend

        :param config: the configuration of the backend
        :type config: dict {'config key': 'value'}
        :param logger: the cherrypy error logger object
        :type logger: python logger
        :param name: id of the backend
        :type name: string
        :param attrslist: list of the backend attributes
        :type attrslist: list of strings
        :param key: the key attribute
        :type key: string
        """
        self.config = config
        self._logger = logger
        self.users = {}
        self.backend_name = name
        admin_user = self.get_param('admin.user', 'admin')
        admin_password = self.get_param('admin.password', 'admin')
        admin_groups = Set(re.split('\W+', self.get_param('admin.groups')))
        basic_user = self.get_param('basic.user', 'user')
        basic_password = self.get_param('basic.password', 'user')
        basic_groups = Set(re.split('\W+', self.get_param('basic.groups')))
        pwd_attr = self.get_param('pwd_attr')
        self.search_attrs = Set(
            re.split('\W+', self.get_param('search_attributes')),
            )
        self.pwd_attr = pwd_attr
        self.admin_user = admin_user
        self.basic_user = basic_user
        self.key = key
        self.users[admin_user] = {
                key: admin_user,
                pwd_attr: admin_password,
                'groups': admin_groups,
                }
        self.users[basic_user] = {
                key: basic_user,
                pwd_attr: basic_password,
                'groups': basic_groups,
                }

    def _check_fix_users(self, username):
        if self.admin_user == username or self.basic_user == username:
            raise Exception('User cannot be modified')

    def auth(self, username, password):
        """ Check authentication against the backend

        :param username: 'key' attribute of the user
        :type username: string
        :param password: password of the user
        :type password: string
        :rtype: boolean (True is authentication success, False otherwise)
        """
        if username not in self.users:
            return False
        elif self.users[username][self.pwd_attr] == password:
            return True
        return False

    def add_user(self, attrs):
        """ Add a user to the backend

        :param attrs: attributes of the user
        :type attrs: dict ({<attr>: <value>})

        .. warning:: raise UserAlreadyExists if user already exists
        """
        username = attrs[self.key]
        if username in self.users:
            raise UserAlreadyExists(username, self.backend_name)
        self.users[username] = attrs
        self.users[username]['groups'] = Set([])

    def del_user(self, username):
        """ Delete a user from the backend

        :param username: 'key' attribute of the user
        :type username: string

        """
        self._check_fix_users(username)
        try:
            del self.users[username]
        except:
            raise UserDoesntExist(username, self.backend_name)

    def set_attrs(self, username, attrs):
        """ Set a list of attributes for a given user

        :param username: 'key' attribute of the user
        :type username: string
        :param attrs: attributes of the user
        :type attrs: dict ({<attr>: <value>})
        """
        self._check_fix_users(username)
        for attr in attrs:
            self.users[username][attr] = attrs[attr]

    def add_to_groups(self, username, groups):
        """ Add a user to a list of groups

        :param username: 'key' attribute of the user
        :type username: string
        :param groups: list of groups
        :type groups: list of strings
        """
        self._check_fix_users(username)
        current_groups = self.users[username]['groups']
        new_groups = current_groups | Set(groups)
        self.users[username]['groups'] = new_groups

    def del_from_groups(self, username, groups):
        """ Delete a user from a list of groups

        :param username: 'key' attribute of the user
        :type username: string
        :param groups: list of groups
        :type groups: list of strings

        .. warning:: raise GroupDoesntExist if group doesn't exist
        """
        self._check_fix_users(username)
        current_groups = self.users[username]['groups']
        new_groups = current_groups - Set(groups)
        self.users[username]['groups'] = new_groups

    def search(self, searchstring):
        """ Search backend for users

        :param searchstring: the search string
        :type searchstring: string
        :rtype: dict of dict ( {<user attr key>: {<attr>: <value>}} )
        """
        ret = {}
        for user in self.users:
            match = False
            for attr in self.search_attrs:
                if attr not in self.users[user]:
                    pass
                elif re.search(searchstring + '.*', self.users[user][attr]):
                    match = True
            if match:
                ret[user] = self.users[user]
        return ret

    def get_user(self, username):
        """ Get a user's attributes

        :param username: 'key' attribute of the user
        :type username: string
        :rtype: dict ( {<attr>: <value>} )

        .. warning:: raise UserDoesntExist if user doesn't exist
        """
        try:
            return self.users[username]
        except:
            raise UserDoesntExist(username, self.backend_name)

    def get_groups(self, username):
        """ Get a user's groups

        :param username: 'key' attribute of the user
        :type username: string
        :rtype: list of groups
        """
        try:
            return self.users[username]['groups']
        except:
            raise UserDoesntExist(username, self.backend_name)
