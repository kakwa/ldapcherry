#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
from sets import Set
from ldapcherry.backend.backendLdap import Backend
from ldapcherry import syslog_error
from ldapcherry.exceptions import *
import cherrypy
import logging
from ldap import SERVER_DOWN

cfg = {
'module'             : 'ldapcherry.backend.ldap',
'groupdn'            : 'ou=Groups,dc=example,dc=org',
'userdn'             : 'ou=People,dc=example,dc=org',
'binddn'             : 'cn=dnscherry,dc=example,dc=org',
'password'           : 'password',
'uri'                : 'ldap://ldap.ldapcherry.org:390',
'ca'                 : './tests/test_env/etc/ldapcherry/TEST-cacert.pem',
'starttls'           : 'off',
'checkcert'          : 'off',
'user_filter_tmpl'   : '(uid=%(username)s)',
'group_filter_tmpl'  : '(member=%(userdn)s)',
'search_filter_tmpl' : '(|(uid=%(searchstring)s*)(sn=%(searchstring)s*))',
'objectclasses'      : 'top, person, organizationalPerson, simpleSecurityObject, posixAccount',
'dn_user_attr'       : 'uid',
}

def syslog_error(msg='', context='',
        severity=logging.INFO, traceback=False):
    pass

cherrypy.log.error = syslog_error
attr = ['shéll', 'cn', 'uid', 'uidNumber', 'gidNumber', 'home', 'userPassword', 'givenName', 'email', 'sn']

cherrypy.log.error = syslog_error

inv = Backend(cfg, cherrypy.log, 'ldap', attr)
print inv.get_user('jwatson')
print inv.get_groups('jwatson')
print inv.search('smit')
user = {
'uid': 'test',
'sn':  'test',
'cn':  'test',
'userPassword': 'test',
'uidNumber': '42',
'gidNumber': '42',
'homeDirectory': '/home/test/'
}
inv.add_user(user)
print inv.get_user('test')
print inv.get_groups('test')
inv.del_user('test')
