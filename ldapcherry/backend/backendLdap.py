# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import cherrypy
import ldap
import ldap.modlist as modlist
import logging
import ldapcherry.backend
import re

class DelUserDontExists(Exception):
    def __init__(self, user):
        self.user = user
        self.log = "cannot remove user, user <%(user)s> does not exist" % { 'user' : user}


class Backend(ldapcherry.backend.Backend):

    def __init__(self, config, logger, name, attrslist, key):
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
        self.dn_user_attr = self.get_param('dn_user_attr')
        self.objectclasses = []
        self.key = key
        for o in re.split('\W+', self.get_param('objectclasses')):
            self.objectclasses.append(self._str(o))
        self.group_attrs = {}
        for param in config:
            name, sep, group = param.partition('.')
            if name == 'group_attr':
                self.group_attrs[group] = self.get_param(param)

        self.attrlist = []
        for a in attrslist:
            self.attrlist.append(self._str(a))

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
                    severity = logging.ERROR,
                    msg = "cannot use starttls with ldaps:// uri (uri: " + self.uri + ")",
                )
                raise e
                #raise cherrypy.HTTPError("500", "Configuration Error, contact administrator")
        return ldap_client

    def _bind(self):
        ldap_client = self._connect()
        try:
            ldap_client.simple_bind_s(self.binddn, self.bindpassword)
        except ldap.INVALID_CREDENTIALS as e:
            self._logger(
                    severity = logging.ERROR,
                    msg = "Configuration error, wrong credentials, unable to connect to ldap with '" + self.binddn + "'",
                )
            ldap_client.unbind_s()
            raise e
        except ldap.SERVER_DOWN as e:
            self._logger(
                    severity = logging.ERROR,
                    msg = "Unable to contact ldap server '" + self.uri + "', check 'auth.ldap.uri' and ssl/tls configuration",
                )
            ldap_client.unbind_s()
            raise e
        return ldap_client

    def _search(self, searchfilter, attrs, basedn):
        ldap_client = self._bind()
        try:
            r = ldap_client.search_s(basedn,
                    ldap.SCOPE_SUBTREE,
                    searchfilter,
                    attrlist=attrs
            )
        except ldap.FILTER_ERROR as e:
            self._logger(
                    severity = logging.ERROR,
                    msg = "Bad search filter, check '" + self.backend_name + ".*_filter_tmpl' params",
                )
            ldap_client.unbind_s()
            raise e
        except ldap.NO_SUCH_OBJECT as e:
            self._logger(
                    severity = logging.ERROR,
                    msg = "Search DN '" + basedn \
                            + "' doesn't exist, check '" \
                            + self.backend_name + ".userdn' or '" \
                            + self.backend_name + ".groupdn'",
                )
            ldap_client.unbind_s()
            raise e

        ldap_client.unbind_s()
        return r

    def _get_user(self, username, attrs=True):
        if attrs:
            a = self.attrlist
        else:
            a = None

        user_filter = self.user_filter_tmpl % {
            'username': username
        }

        r = self._search(user_filter, a, self.userdn)

        if len(r) == 0:
            return None

        if attrs:
            dn_entry = r[0]
        else:
            dn_entry = r[0][0]
        return dn_entry

    def _str(self, s):
            try:
                return str(s)
            except UnicodeEncodeError:
                return unicode(s).encode('unicode_escape')

    def auth(self, username, password):

        binddn = self._get_user(username, False)
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

    def add_user(self, attrs):
        ldap_client = self._bind()
        attrs_str = {}
        for a in attrs:
            attrs_str[self._str(a)] = self._str(attrs[a])
        attrs_str['objectClass'] = self.objectclasses
        dn = self.dn_user_attr + '=' + attrs[self.dn_user_attr] + ',' + self.userdn
        ldif = modlist.addModlist(attrs_str)
        try:
            ldap_client.add_s(dn,ldif)
        except ldap.OBJECT_CLASS_VIOLATION as e:
            info = e[0]['info']
            desc = e[0]['desc']
            self._logger(
                    severity = logging.ERROR,
                    msg = "Configuration error, " + desc + ", " + info,
                )
            ldap_client.unbind_s()
            raise e
        except ldap.INSUFFICIENT_ACCESS as e:
            info = e[0]['info']
            desc = e[0]['desc']
            self._logger(
                    severity = logging.ERROR,
                    msg = "Access error, " + desc + ", " + info,
                )
            ldap_client.unbind_s()
            raise e
        except ldap.ALREADY_EXISTS as e:
            desc = e[0]['desc']
            self._logger(
                    severity = logging.ERROR,
                    msg = "adding user failed, " + desc,
                )
            ldap_client.unbind_s()
            raise e
        ldap_client.unbind_s()

    def del_user(self, username):
        ldap_client = self._bind()
        dn = self._get_user(username, False)
        if not dn is None:
            ldap_client.delete_s(dn)
        else:
            raise DelUserDontExists(username)
        ldap_client.unbind_s()

    def set_attrs(self, attrs, username):
        ldap_client = self._bind()
        tmp = self._get_user(username, True)
        dn = tmp[0]
        old_attrs = tmp[1] 
        for attr in attrs: 
            content = attrs[attr]
            new = { attr : content }
            if attr in old_attrs:
                old = { attr: old_attrs[attr]}
                ldif = modlist.modifyModlist(old,new)
                ldap_client.modify_s(dn,ldif)
            else:
                ldif = modlist.addModlist({ attr : content })
                ldap_client.add_s(dn,ldif)
        ldap_client.unbind_s()

    def add_to_group(self, username, groups):
        ldap_client = self._bind()
        tmp = self._get_user(username, True)
        dn = tmp[0]
        attrs = tmp[1] 
        attrs['dn'] = dn
        for group in groups:
            for attr in self.group_attrs:
                content = self.group_attrs[attr] % attrs
                ldif = modlist.addModlist({ attr : content })
                ldap_client.add_s(group,ldif)
        ldap_client.unbind_s()
            
    def rm_from_group(self, username):
        ldap_client = self._bind()
        tmp = self._get_user(username, True)
        dn = tmp[0]
        attrs = tmp[1] 
        attrs['dn'] = dn
        for group in groups:
            for attr in self.group_attrs:
                content = self.group_attrs[attr] % attrs
                ldif = modlist.addModlist({ attr : content })
                ldap_client.delete_s(group,ldif)
        ldap_client.unbind_s()

    def search(self, searchstring):
        ret = {}

        searchfilter = self.search_filter_tmpl % {
            'searchstring': searchstring
        }
        for u in self._search(searchfilter, None, self.userdn):
            attrs = {}
            attrs_tmp = u[1]
            for attr in attrs_tmp:
                value_tmp = attrs_tmp[attr]
                if len(value_tmp) == 1:
                    attrs[attr] = value_tmp[0]
                else:
                    attrs[attr] = value_tmp

            if self.key in attrs:
                ret[attrs[self.key]] = attrs
        return ret

    def get_user(self, username):
        ret = {}
        attrs_tmp = self._get_user(username)[1]
        for attr in attrs_tmp:
            value_tmp = attrs_tmp[attr]
            if len(value_tmp) == 1:
                ret[attr] = value_tmp[0]
            else:
                ret[attr] = value_tmp
        return ret

    def get_groups(self, username):
        userdn = self._get_user(username, False)

        searchfilter = self.group_filter_tmpl % {
            'userdn': userdn,
            'username': username
        }

        groups = self._search(searchfilter, None, self.groupdn)
        ret = []
        for entry in groups:
            ret.append(entry[0])
        return ret
