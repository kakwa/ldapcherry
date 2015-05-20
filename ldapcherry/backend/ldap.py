# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import cherrypy
import ldap
import logging
import ldapcherry.backend

class Backend(ldapcherry.backend.Backend):

    def __init__(self, config, logger):
        self.config = config

    def auth(self, username, password):

        binddn = get_user(username)
        if binddn:
            ldap_client = self._connect()
            try:
                ldap_client.simple_bind_s(binddn, password)
            except ldap.INVALID_CREDENTIALS:
                ldap_client.unbind_s()
                return False
            ldap_client.unbind_s()
            return True
        else:
            return False

    def add_to_group(self):
        pass

    def set_attrs(self, attrs):
        pass

    def rm_from_group(self):
        pass

    def add_user(self, username):
        pass

    def del_user(self, username):
        pass

    def get_user(self, username):
        ldap_client = self._connect()
        try:
            ldap_client.simple_bind_s(self.binddn, self.bindpassword)
        except ldap.INVALID_CREDENTIALS:
            self._logger(
                    logging.ERROR,
                    "Configuration error, wrong credentials, unable to connect to ldap with '" + self.binddn + "'"
                )
            raise cherrypy.HTTPError("500", "Configuration Error, contact administrator")
        except ldap.SERVER_DOWN:
            self._logger(
                    logging.ERROR,
                    "Unable to contact ldap server '" + self.uri + "', check 'auth.ldap.uri' and ssl/tls configuration"
                )
            return False

        user_filter = self.config['user_filter_tmpl'] % {
            'login': username
            }

        r = ldap_client.search_s(self.userdn,
                ldap.SCOPE_SUBTREE,
                user_filter
                 )
        if len(r) == 0:
            ldap_client.unbind_s()
            return False

        dn_entry = r[0][0]
        return dn_entry

    def _connect(self):
        ldap_client = ldap.initialize(self.config['uri'])
        ldap_client.set_option(ldap.OPT_REFERRALS, 0)
        if self.config['starttls'] == 'on':
           ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
        if self.config['starttls'] == 'on':
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
        if self.ca:
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.config['ca'])
        if self.checkcert == 'off':
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
        else:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_DEMAND)

        if self.config['starttls'] == 'on':
            try:
                ldap_client.start_tls_s()
            except ldap.OPERATIONS_ERROR:
                self._logger(
                    logging.ERROR,
                    "cannot use starttls with ldaps:// uri (uri: " + self.uri + ")"
                )
                raise cherrypy.HTTPError("500", "Configuration Error, contact administrator")
        return ldap_client
