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

    def __init__(self, config, logger, name, attrslist):
        self.config = config
        self._logger = logger
        self.backend_name = name
        self.binddn = self.get_param('binddn')
        self.bindpassword = self.get_param('password')
        self.ca = self.get_param('ca', False)
        self.checkcert = self.get_param('checkcert', 'on')
        self.starttls = self.get_param('starttls', 'off')
        self.uri = self.get_param('uri')
        self.timeout = self.get_param('timeout', 1)
        self.userdn = self.get_param('userdn')
        self.groupdn = self.get_param('groupdn')
        self.user_filter_tmpl = self.get_param('user_filter_tmpl')
        self.group_filter_tmpl = self.get_param('group_filter_tmpl')
        self.search_filter_tmpl = self.get_param('search_filter_tmpl')
        self.attrlist = []
        for a in attrslist:
            try:
                self.attrlist.append(str(a))
            except UnicodeEncodeError:
                tmp = unicode(a).encode('unicode_escape')
                self.attrlist.append(tmp)

    def auth(self, username, password):

        binddn = self.get_user(username, False)
        if not binddn is None:
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

    def rm_from_group(self,username):
        pass

    def add_user(self, username):
        pass

    def del_user(self, username):
        pass

    def _search(self, searchfilter, attrs):
        ldap_client = self._connect()
        try:
            ldap_client.simple_bind_s(self.binddn, self.bindpassword)
        except ldap.INVALID_CREDENTIALS as e:
            self._logger(
                    logging.ERROR,
                    "Configuration error, wrong credentials, unable to connect to ldap with '" + self.binddn + "'",
                )
            ldap_client.unbind_s()
            raise e
        except ldap.SERVER_DOWN as e:
            self._logger(
                    logging.ERROR,
                    "Unable to contact ldap server '" + self.uri + "', check 'auth.ldap.uri' and ssl/tls configuration",
                )
            ldap_client.unbind_s()
            raise e 

        try:
            r = ldap_client.search_s(self.userdn,
                    ldap.SCOPE_SUBTREE,
                    searchfilter,
                    attrlist=attrs
            )
        except ldap.FILTER_ERROR as e:
            self._logger(
                    logging.ERROR,
                    "Bad search filter, check '" + self.backend_name + ".*_filter_tmpl' params",
                )
            ldap_client.unbind_s()
            raise e

        ldap_client.unbind_s()
        return r


    def search(self, searchstring):

        searchfilter = self.search_filter_tmpl % {
            'searchstring': searchstring
        }

        return self._search(searchfilter, None)

    def get_user(self, username, attrs=True):
        if attrs:
            a = self.attrlist
        else:
            a = None

        user_filter = self.user_filter_tmpl % {
            'username': username
        }

        r = self._search(user_filter, a)

        if len(r) == 0:
            return None

        if attrs:
            dn_entry = r[0]
        else:
            dn_entry = r[0][0]
        return dn_entry

    def _connect(self):
        ldap_client = ldap.initialize(self.uri)
        ldap_client.set_option(ldap.OPT_REFERRALS, 0)
        ldap_client.set_option(ldap.OPT_TIMEOUT, self.timeout)
        if self.starttls == 'on':
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
        else:
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, False)
        if self.ca and self.checkcert == 'on':
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.ca)
        #else:
        #    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, '')
        if self.checkcert == 'off':
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
        else:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_DEMAND)
        if self.starttls == 'on': 
            try:
                ldap_client.start_tls_s()
            except ldap.OPERATIONS_ERROR as e:
                self._logger(
                    logging.ERROR,
                    "cannot use starttls with ldaps:// uri (uri: " + self.uri + ")",
                )
                raise e
                #raise cherrypy.HTTPError("500", "Configuration Error, contact administrator")
        return ldap_client
