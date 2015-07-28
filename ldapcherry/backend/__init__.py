# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

from ldapcherry.exceptions import MissingParameter


class Backend(object):

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
        raise Exception()

    def auth(self, username, password):
        """ Check authentication against the backend

        :param username: 'key' attribute of the user
        :type username: string
        :param password: password of the user
        :type password: string
        :rtype: boolean (True is authentication success, False otherwise)
        """
        return False

    def add_user(self, attrs):
        """ Add a user to the backend

        :param attrs: attributes of the user
        :type attrs: dict ({<attr>: <value>})

        .. warning:: raise UserAlreadyExists if user already exists
        """
        pass

    def del_user(self, username):
        """ Delete a user from the backend

        :param username: 'key' attribute of the user
        :type username: string

        """
        pass

    def set_attrs(self, username, attrs):
        """ Set a list of attributes for a given user

        :param username: 'key' attribute of the user
        :type username: string
        :param attrs: attributes of the user
        :type attrs: dict ({<attr>: <value>})
        """
        pass

    def add_to_groups(self, username, groups):
        """ Add a user to a list of groups

        :param username: 'key' attribute of the user
        :type username: string
        :param groups: list of groups
        :type groups: list of strings
        """
        pass

    def del_from_groups(self, username, groups):
        """ Delete a user from a list of groups

        :param username: 'key' attribute of the user
        :type username: string
        :param groups: list of groups
        :type groups: list of strings

        .. warning:: raise GroupDoesntExist if group doesn't exist
        """
        pass

    def search(self, searchstring):
        """ Search backend for users

        :param searchstring: the search string
        :type searchstring: string
        :rtype: dict of dict ( {<user attr key>: {<attr>: <value>}} )
        """
        return {}

    def get_user(self, username):
        """ Get a user's attributes

        :param username: 'key' attribute of the user
        :type username: string
        :rtype: dict ( {<attr>: <value>} )

        .. warning:: raise UserDoesntExist if user doesn't exist
        """
        return {}

    def get_groups(self, username):
        """ Get a user's groups

        :param username: 'key' attribute of the user
        :type username: string
        :rtype: list of groups
        """
        return []

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
            raise MissingParameter('backends', self.backend_name + '.' + param)
