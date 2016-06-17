# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import cherrypy
import ldap
import ldap.modlist as modlist
import ldap.filter
import logging
import ldapcherry.backend
from ldapcherry.exceptions import UserDoesntExist, \
    GroupDoesntExist, \
    UserAlreadyExists
import os
import re


class CaFileDontExist(Exception):
    def __init__(self, cafile):
        self.cafile = cafile
        self.log = "CA file %(cafile)s does not exist" % {'cafile': cafile}

NO_ATTR = 0
DISPLAYED_ATTRS = 1
LISTED_ATTRS = 2
ALL_ATTRS = 3


class Backend(ldapcherry.backend.Backend):

    def __init__(self, config, logger, name, attrslist, key):
        """Backend initialization"""
        # Recover all the parameters
        self.config = config
        self._logger = logger
        self.backend_name = name
        self.backend_display_name = self.get_param('display_name')
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
        # objectclasses parameter is a coma separated list in configuration
        # split it to get a real list, and convert it to bytes
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

    # exception handler (mainly to log something meaningful)
    def _exception_handler(self, e):
        """ Exception handling"""
        et = type(e)
        if et is ldap.OPERATIONS_ERROR:
            self._logger(
                severity=logging.ERROR,
                msg="cannot use starttls with ldaps://"
                    " uri (uri: " + self.uri + ")",
            )
        elif et is ldap.INVALID_CREDENTIALS:
            self._logger(
                severity=logging.ERROR,
                msg="Configuration error, wrong credentials,"
                " unable to connect to ldap with '" + self.binddn + "'",
            )
        elif et is ldap.SERVER_DOWN:
            self._logger(
                severity=logging.ERROR,
                msg="Unable to contact ldap server '" +
                    self.uri +
                    "', check 'auth.ldap.uri'"
                    " and ssl/tls configuration",
                )
        elif et is ldap.FILTER_ERROR:
            self._logger(
                severity=logging.ERROR,
                msg="Bad search filter, check '" +
                    self.backend_name +
                    ".*_filter_tmpl' params",
                )
        elif et is ldap.NO_SUCH_OBJECT:
            self._logger(
                severity=logging.ERROR,
                msg="DN doesn't exist, check '" +
                    self.backend_name +
                    ".userdn'or '" +
                    self.backend_name +
                    ".groupdn'",
                )
        elif et is ldap.OBJECT_CLASS_VIOLATION:
            info = e[0]['info']
            desc = e[0]['desc']
            self._logger(
                severity=logging.ERROR,
                msg="Configuration error, " + desc + ", " + info,
                )
        elif et is ldap.INSUFFICIENT_ACCESS:
            self._logger(
                severity=logging.ERROR,
                msg="Access error on '" +
                    self.backend_name +
                    "' backend, please check your acls in backend " +
                    self.backend_name,
                )
        elif et is ldap.ALREADY_EXISTS:
            desc = e[0]['desc']
            self._logger(
                severity=logging.ERROR,
                msg="adding user failed, " + desc,
                )
        else:
            self._logger(
                severity=logging.ERROR,
                msg="unknow exception in backend " + self.backend_name,
                )
        raise

    def _connect(self):
        """Initialize an ldap client"""
        ldap_client = ldap.initialize(self.uri)
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        ldap.set_option(ldap.OPT_TIMEOUT, self.timeout)
        if self.starttls == 'on':
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
        else:
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, False)
        # set the CA file if declared and if necessary
        if self.ca and self.checkcert == 'on':
            # check if the CA file actually exists
            if os.path.isfile(self.ca):
                ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.ca)
            else:
                raise CaFileDontExist(self.ca)
        if self.checkcert == 'off':
            # this is dark magic
            # remove any of these two lines and it doesn't work
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            ldap_client.set_option(
                ldap.OPT_X_TLS_REQUIRE_CERT,
                ldap.OPT_X_TLS_NEVER
                )
        else:
            # this is even darker magic
            ldap_client.set_option(
                ldap.OPT_X_TLS_REQUIRE_CERT,
                ldap.OPT_X_TLS_DEMAND
                )
            # it doesn't make sense to set it to never
            # (== don't check certifate)
            # but it only works with this option...
            # ... and it checks the certificat
            # (I've lost my sanity over this)
            ldap.set_option(
                ldap.OPT_X_TLS_REQUIRE_CERT,
                ldap.OPT_X_TLS_NEVER
                )
        if self.starttls == 'on':
            try:
                ldap_client.start_tls_s()
            except Exception as e:
                self._exception_handler(e)
        return ldap_client

    def _bind(self):
        """bind to the ldap with the technical account"""
        ldap_client = self._connect()
        try:
            ldap_client.simple_bind_s(self.binddn, self.bindpassword)
        except Exception as e:
            ldap_client.unbind_s()
            self._exception_handler(e)
        return ldap_client

    def _search(self, searchfilter, attrs, basedn):
        """Generic search"""
        if attrs == NO_ATTR:
            attrlist = []
        elif attrs == DISPLAYED_ATTRS:
            # fix me later (to much attributes)
            attrlist = self.attrlist
        elif attrs == LISTED_ATTRS:
            attrlist = self.attrlist
        elif attrs == ALL_ATTRS:
            attrlist = None
        else:
            attrlist = None

        # bind and search the ldap
        ldap_client = self._bind()
        try:
            r = ldap_client.search_s(
                basedn,
                ldap.SCOPE_SUBTREE,
                searchfilter,
                attrlist=attrlist
                )
        except Exception as e:
            ldap_client.unbind_s()
            self._exception_handler(e)

        ldap_client.unbind_s()

        # python-ldap doesn't know utf-8,
        # it treates everything as bytes.
        # So it's necessary to reencode
        # it's output in utf-8.
        ret = []
        for entry in r:
            uni_dn = self._uni(entry[0])
            uni_attrs = {}
            for attr in entry[1]:
                if type(entry[1][attr]) is list:
                    tmp = []
                    for value in entry[1][attr]:
                        tmp.append(self._uni(value))
                else:
                    tmp = self._uni(entry[1][attr])
                uni_attrs[self._uni(attr)] = tmp
            ret.append((uni_dn, uni_attrs))
        return ret

    def _get_user(self, username, attrs=ALL_ATTRS):
        """Get a user from the ldap"""

        username = ldap.filter.escape_filter_chars(username)
        user_filter = self.user_filter_tmpl % {
            'username': username
        }
        user_filter = self._str(user_filter)
        r = self._search(user_filter, attrs, self.userdn)

        if len(r) == 0:
            return None

        # if NO_ATTR, only return the DN
        if attrs == NO_ATTR:
            dn_entry = r[0][0]
        # in other cases, return everything (dn + attributes)
        else:
            dn_entry = r[0]
        return dn_entry
    # python-ldap talks in bytes,
    # as the rest of ldapcherry talks in unicode utf-8:
    # * everything passed to python-ldap must be converted to bytes
    # * everything coming from python-ldap must be converted to unicode

    def _str(self, s):
        """unicode -> bytes conversion"""
        if s is None:
            return None
        return s.encode('utf-8')

    def _uni(self, s):
        """bytes -> unicode conversion"""
        if s is None:
            return None
        return s.decode('utf-8', 'ignore')

    def auth(self, username, password):
        """Authentication of a user"""

        binddn = self._str(self._get_user(username, NO_ATTR))
        if binddn is not None:
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

    def attrs_pretreatment(self, attrs):
        attrs_str = {}
        for a in attrs:
            attrs_str[self._str(a)] = self._str(attrs[a])
        return attrs_str

    def add_user(self, attrs):
        """add a user"""
        ldap_client = self._bind()
        # encoding crap
        attrs_str = self.attrs_pretreatment(attrs)

        attrs_str['objectClass'] = self.objectclasses
        # construct is DN
        dn = \
            self._str(self.dn_user_attr) + \
            '=' + \
            self._str(attrs[self.dn_user_attr]) + \
            ',' + \
            self._str(self.userdn)
        # gen the ldif fir add_s and add the user
        ldif = modlist.addModlist(attrs_str)
        try:
            ldap_client.add_s(dn, ldif)
        except ldap.ALREADY_EXISTS as e:
            raise UserAlreadyExists(attrs[self.key], self.backend_name)
        except Exception as e:
            ldap_client.unbind_s()
            self._exception_handler(e)
        ldap_client.unbind_s()

    def del_user(self, username):
        """delete a user"""
        ldap_client = self._bind()
        # recover the user dn
        dn = self._str(self._get_user(username, NO_ATTR))
        # delete
        if dn is not None:
            ldap_client.delete_s(dn)
        else:
            ldap_client.unbind_s()
            raise UserDoesntExist(username, self.backend_name)
        ldap_client.unbind_s()

    def set_attrs(self, username, attrs):
        """ Set user attributes"""
        ldap_client = self._bind()
        tmp = self._get_user(username, ALL_ATTRS)
        dn = self._str(tmp[0])
        old_attrs = tmp[1]
        for attr in attrs:
            bcontent = self._str(attrs[attr])
            battr = self._str(attr)
            new = {battr: bcontent}
            # if attr is dn entry, use rename
            if attr.lower() == self.dn_user_attr.lower():
                ldap_client.rename_s(
                    dn,
                    ldap.dn.dn2str([[(battr, bcontent, 1)]])
                    )
                dn = ldap.dn.dn2str(
                    [[(battr, bcontent, 1)]] + ldap.dn.str2dn(dn)[1:]
                    )
            else:
                # if attr is already set, replace the value
                # (see dict old passed to modifyModlist)
                if attr in old_attrs:
                    if type(old_attrs[attr]) is list:
                        tmp = []
                        for value in old_attrs[attr]:
                            tmp.append(self._str(value))
                        bold_value = tmp
                    else:
                        bold_value = self._str(old_attrs[attr])
                    old = {battr: bold_value}
                # attribute is not set, just add it
                else:
                    old = {}
                ldif = modlist.modifyModlist(old, new)
                try:
                    ldap_client.modify_s(dn, ldif)
                except Exception as e:
                    ldap_client.unbind_s()
                    self._exception_handler(e)

        ldap_client.unbind_s()

    def add_to_groups(self, username, groups):
        ldap_client = self._bind()
        # recover dn of the user and his attributes
        tmp = self._get_user(username, ALL_ATTRS)
        dn = tmp[0]
        attrs = tmp[1]
        attrs['dn'] = dn
        dn = self._str(tmp[0])
        # add user to all groups
        for group in groups:
            group = self._str(group)
            # iterate on group membership attributes
            for attr in self.group_attrs:
                # fill the content template
                content = self._str(self.group_attrs[attr] % attrs)
                self._logger(
                    severity=logging.DEBUG,
                    msg="%(backend)s: adding user '%(user)s'"
                        " with dn '%(dn)s' to group '%(group)s' by"
                        " setting '%(attr)s' to '%(content)s'" % {
                            'user': username,
                            'dn': self._uni(dn),
                            'group': self._uni(group),
                            'attr': attr,
                            'content': self._uni(content),
                            'backend': self.backend_name
                            }
                )
                ldif = modlist.modifyModlist({}, {attr: content})
                try:
                    ldap_client.modify_s(group, ldif)
                # if already member, not a big deal, just log it and continue
                except ldap.TYPE_OR_VALUE_EXISTS as e:
                    self._logger(
                        severity=logging.INFO,
                        msg="%(backend)s: user '%(user)s'"
                            " already member of group '%(group)s'"
                            " (attribute '%(attr)s')" % {
                                'user': username,
                                'group': self._uni(group),
                                'attr': attr,
                                'backend': self.backend_name
                                }
                    )
                except ldap.NO_SUCH_OBJECT as e:
                    raise GroupDoesntExist(group, self.backend_name)
                except Exception as e:
                    ldap_client.unbind_s()
                    self._exception_handler(e)
        ldap_client.unbind_s()

    def del_from_groups(self, username, groups):
        """Delete user from groups"""
        # it follows the same logic than add_to_groups
        # but with MOD_DELETE
        ldap_client = self._bind()
        tmp = self._get_user(username, ALL_ATTRS)
        dn = tmp[0]
        attrs = tmp[1]
        attrs['dn'] = dn
        dn = self._str(tmp[0])
        for group in groups:
            group = self._str(group)
            for attr in self.group_attrs:
                content = self._str(self.group_attrs[attr] % attrs)
                ldif = [(ldap.MOD_DELETE, attr, content)]
                try:
                    ldap_client.modify_s(group, ldif)
                except ldap.NO_SUCH_ATTRIBUTE as e:
                    self._logger(
                        severity=logging.INFO,
                        msg="%(backend)s: user '%(user)s'"
                        " wasn't member of group '%(group)s'"
                        " (attribute '%(attr)s')" % {
                            'user': username,
                            'group': self._uni(group),
                            'attr': attr,
                            'backend': self.backend_name
                            }
                    )
                except Exception as e:
                    ldap_client.unbind_s()
                    self._exception_handler(e)
        ldap_client.unbind_s()

    def search(self, searchstring):
        """Search users"""
        # escape special char to avoid injection
        searchstring = ldap.filter.escape_filter_chars(searchstring)
        # fill the search string template
        searchfilter = self.search_filter_tmpl % {
            'searchstring': searchstring
        }

        ret = {}
        # search an process the result a little
        for u in self._search(searchfilter, DISPLAYED_ATTRS, self.userdn):
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
        """Gest a specific user"""
        ret = {}
        tmp = self._get_user(username, ALL_ATTRS)
        if tmp is None:
            raise UserDoesntExist(username, self.backend_name)
        attrs_tmp = tmp[1]
        for attr in attrs_tmp:
            value_tmp = attrs_tmp[attr]
            if len(value_tmp) == 1:
                ret[attr] = value_tmp[0]
            else:
                ret[attr] = value_tmp
        return ret

    def get_groups(self, username):
        """Get all groups of a user"""
        username = ldap.filter.escape_filter_chars(username)
        userdn = self._get_user(username, NO_ATTR)

        searchfilter = self.group_filter_tmpl % {
            'userdn': userdn,
            'username': username
        }

        groups = self._search(searchfilter, NO_ATTR, self.groupdn)
        ret = []
        for entry in groups:
            ret.append(entry[0])
        return ret
