#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# ldapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

# Generic imports
import sys
import re
import traceback
import json
import logging
import logging.handlers
from operator import itemgetter
from socket import error as socket_error
import base64

from exceptions import *
from ldapcherry.roles import Roles
from ldapcherry.attributes import Attributes

# Cherrypy http framework imports
import cherrypy
from cherrypy.lib.httputil import parse_query_string

# Mako template engines imports
from mako.template import Template
from mako import lookup
from sets import Set

SESSION_KEY = '_cp_username'


# Custom log function to overrige weird error.log function
# of cherrypy
def syslog_error(
        msg='',
        context='',
        severity=logging.INFO,
        traceback=False
        ):

    if traceback and msg == '':
        msg = 'python exception'
    if context == '':
        cherrypy.log.error_log.log(severity, msg)
    else:
        cherrypy.log.error_log.log(
            severity,
            ' '.join((context, msg))
            )
    import traceback
    if traceback:
        try:
            exc = sys.exc_info()
            if exc == (None, None, None):
                cherrypy.log.error_log.log(severity, msg)
            # log each line of the exception
            # in a separate log for lisibility
            for l in traceback.format_exception(*exc):
                cherrypy.log.error_log.log(severity, l)
        finally:
            del exc


class LdapCherry(object):

    def _handle_exception(self, e):
        if hasattr(e, 'log'):
            cherrypy.log.error(
                msg=e.log,
                severity=logging.ERROR
            )
        else:
            cherrypy.log.error(
                msg="unkwon exception: '%(e)s'" % {'e': str(e)},
                severity=logging.ERROR
            )
        # log the traceback as 'debug'
        cherrypy.log.error(
            msg='',
            severity=logging.DEBUG,
            traceback=True
            )

    def _get_param(self, section, key, config, default=None):
        """ Get configuration parameter "key" from config
        @str section: the section of the config file
        @str key: the key to get
        @dict config: the configuration (dictionnary)
        @str default: the default value if parameter "key" is not present
        @rtype: str (value of config['key'] if present default otherwith
        """
        if section in config and key in config[section]:
            return config[section][key]
        if default is not None:
            return default
        else:
            raise MissingParameter(section, key)

    def _get_groups(self, username):
        """ Get groups of a user
        @str username: name of the user
        @rtype: dict, format { '<backend>': [<list of groups>] }
        """
        ret = {}
        for b in self.backends:
            ret[b] = self.backends[b].get_groups(username)
        cherrypy.log.error(
            msg="user '" + username + "' groups: " + str(ret),
            severity=logging.DEBUG,
        )
        return ret

    def _get_roles(self, username):
        """ Get roles of a user
        @str username: name of the user
        @rtype: dict, format { 'roles': [<list of roles>],
            'unusedgroups': [<list of groups not matching roles>] }
        """
        groups = self._get_groups(username)
        user_roles = self.roles.get_roles(groups)
        cherrypy.log.error(
            msg="user '" + username + "' roles: " + str(user_roles),
            severity=logging.DEBUG,
        )
        return user_roles

    def _is_admin(self, username):
        """ Check if a user is an ldapcherry administrator
        @str username: name of the user
        @rtype: bool, True if administrator, False otherwise
        """
        roles = self._get_roles(username)
        return self.roles.is_admin(roles['roles'])

    def _check_backends(self):
        """ Check that every backend in roles and attributes
        is declared in main configuration
        """
        backends = self.backends_params.keys()
        for b in self.roles.get_backends():
            if b not in backends:
                raise MissingBackend(b)
        for b in self.roles.get_backends():
            if b not in backends:
                raise MissingBackend(b)

    def _init_backends(self, config):
        """ Init all backends
        @dict: configuration of ldapcherry
        """
        self.backends_params = {}
        self.backends = {}
        for entry in config['backends']:
            # split at the first dot
            backend, sep, param = entry.partition('.')
            value = config['backends'][entry]
            if backend not in self.backends_params:
                self.backends_params[backend] = {}
            self.backends_params[backend][param] = value
        for backend in self.backends_params:
            params = self.backends_params[backend]
            # Loading the backend module
            try:
                module = params['module']
            except:
                raise MissingParameter('backends', backend + '.module')
            try:
                bc = __import__(module, globals(), locals(), ['Backend'], -1)
            except:
                raise BackendModuleLoadingFail(module)
            try:
                attrslist = self.attributes.get_backend_attributes(backend)
                key = self.attributes.get_backend_key(backend)
                self.backends[backend] = bc.Backend(
                    params,
                    cherrypy.log,
                    backend,
                    attrslist,
                    key,
                    )
            except MissingParameter as e:
                raise e
            except:
                raise BackendModuleInitFail(module)

    def _init_ppolicy(self, config):
        module = self._get_param(
            'ppolicy',
            'ppolicy.module',
            config,
            'ldapcherry.ppolicy'
        )
        try:
            pp = __import__(module, globals(), locals(), ['PPolicy'], -1)
        except:
            raise BackendModuleLoadingFail(module)
        if 'ppolicy' in config:
            ppcfg = config['ppolicy']
        else:
            ppcfg = {}
        self.ppolicy = pp.PPolicy(ppcfg, cherrypy.log)

    def _init_auth(self, config):
        """ Init authentication
        @dict: configuration of ldapcherry
        """
        self.auth_mode = self._get_param('auth', 'auth.mode', config)
        if self.auth_mode in ['and', 'or', 'none']:
            pass
        elif self.auth_mode == 'custom':
            # load custom auth module
            auth_module = self._get_param('auth', 'auth.module', config)
            auth = __import__(auth_module, globals(), locals(), ['Auth'], -1)
            self.auth = auth.Auth(config['auth'], cherrypy.log)
        else:
            raise WrongParamValue(
                'auth.mode',
                'auth',
                ['and', 'or', 'none', 'custom'],
                )

        self.roles_file = self._get_param('roles', 'roles.file', config)
        cherrypy.log.error(
            msg="loading roles file '%(file)s'" % {'file': self.roles_file},
            severity=logging.DEBUG
        )
        self.roles = Roles(self.roles_file)

    def _set_access_log(self, config, level):
        """ Configure access logs
        """
        access_handler = self._get_param(
            'global',
            'log.access_handler',
            config,
            'syslog',
            )

        # log format for syslog
        syslog_formatter = logging.Formatter(
            "ldapcherry[%(process)d]: %(message)s"
            )

        # replace access log handler by a syslog handler
        if access_handler == 'syslog':
            cherrypy.log.access_log.handlers = []
            handler = logging.handlers.SysLogHandler(
                address='/dev/log',
                facility='user',
                )
            handler.setFormatter(syslog_formatter)
            cherrypy.log.access_log.addHandler(handler)

        # if file, we keep the default
        elif access_handler == 'file':
            pass

        # replace access log handler by a null handler
        elif access_handler == 'none':
            cherrypy.log.access_log.handlers = []
            handler = logging.NullHandler()
            cherrypy.log.access_log.addHandler(handler)

        # set log level
        cherrypy.log.access_log.setLevel(level)

    def _set_error_log(self, config, level):
        """ Configure error logs
        """
        error_handler = self._get_param(
            'global',
            'log.error_handler',
            config,
            'syslog'
            )

        # log format for syslog
        syslog_formatter = logging.Formatter(
            "ldapcherry[%(process)d]: %(message)s",
            )

        # replacing the error handler by a syslog handler
        if error_handler == 'syslog':
            cherrypy.log.error_log.handlers = []

            # redefining log.error method because cherrypy does weird
            # things like adding the date inside the message
            # or adding space even if context is empty
            # (by the way, what's the use of "context"?)
            cherrypy.log.error = syslog_error

            handler = logging.handlers.SysLogHandler(
                address='/dev/log',
                facility='user',
                )
            handler.setFormatter(syslog_formatter)
            cherrypy.log.error_log.addHandler(handler)

        # if file, we keep the default
        elif error_handler == 'file':
            pass

        # replacing the error handler by a null handler
        elif error_handler == 'none':
            cherrypy.log.error_log.handlers = []
            handler = logging.NullHandler()
            cherrypy.log.error_log.addHandler(handler)

        # set log level
        cherrypy.log.error_log.setLevel(level)

    def _get_loglevel(self, level):
        """ return logging level object
        corresponding to a given level passed as
        a string
        @str level: name of a syslog log level
        @rtype: logging, logging level from logging module
        """
        if level == 'debug':
            return logging.DEBUG
        elif level == 'notice':
            return logging.INFO
        elif level == 'info':
            return logging.INFO
        elif level == 'warning' or level == 'warn':
            return logging.WARNING
        elif level == 'error' or level == 'err':
            return logging.ERROR
        elif level == 'critical' or level == 'crit':
            return logging.CRITICAL
        elif level == 'alert':
            return logging.CRITICAL
        elif level == 'emergency' or level == 'emerg':
            return logging.CRITICAL
        else:
            return logging.INFO

    def _auth(self, user, password):
        """ authenticate a user
        @str user: login of the user
        @str password: password of the user
        @rtype: dict, {'connected': <boolean, True if connection succeded>,
            'isadmin': <True if user is ldapcherry administrator>}
        """
        if self.auth_mode == 'none':
            return {'connected': True, 'isadmin': True}
        elif self.auth_mode == 'and':
            ret1 = True
            for b in self.backends:
                ret1 = self.backends[b].auth(user, password) and ret1
        elif self.auth_mode == 'or':
            ret1 = False
            for b in self.backends:
                ret1 = self.backends[b].auth(user, password) or ret1
        elif self.auth_mode == 'custom':
            ret1 = self.auth.auth(user, password)
        else:
            raise Exception()
        if not ret1:
            return {'connected': False, 'isadmin': False}
        else:
            isadmin = self._is_admin(user)
            return {'connected': True, 'isadmin': isadmin}

    def _load_templates(self, config):
        """ load templates
        @dict: configuration of ldapcherry
        """
        # definition of the template directory
        self.template_dir = self._get_param(
            'resources',
            'templates.dir',
            config
            )
        cherrypy.log.error(
            msg="loading templates from dir '%(dir)s'" %
                {'dir': self.template_dir},
            severity=logging.DEBUG
        )
        # preload templates
        self.temp_lookup = lookup.TemplateLookup(
            directories=self.template_dir, input_encoding='utf-8'
            )
        self.temp_index = \
            self.temp_lookup.get_template('index.tmpl')
        self.temp_error = \
            self.temp_lookup.get_template('error.tmpl')
        self.temp_login = \
            self.temp_lookup.get_template('login.tmpl')
        self.temp_searchadmin = \
            self.temp_lookup.get_template('searchadmin.tmpl')
        self.temp_searchuser = \
            self.temp_lookup.get_template('searchuser.tmpl')
        self.temp_adduser = \
            self.temp_lookup.get_template('adduser.tmpl')
        self.temp_roles = \
            self.temp_lookup.get_template('roles.tmpl')
        self.temp_groups = \
            self.temp_lookup.get_template('groups.tmpl')
        self.temp_form = \
            self.temp_lookup.get_template('form.tmpl')
        self.temp_selfmodify = \
            self.temp_lookup.get_template('selfmodify.tmpl')
        self.temp_modify = \
            self.temp_lookup.get_template('modify.tmpl')

    def reload(self, config=None):
        """ load/reload configuration
        @dict: configuration of ldapcherry
        """
        try:
            # log configuration handling
            # get log level
            # (if not in configuration file, log level is set to debug)
            level = self._get_loglevel(
                self._get_param(
                    'global',
                    'log.level',
                    config,
                    'debug',
                    )
                )
            # configure access log
            self._set_access_log(config, level)
            # configure error log
            self._set_error_log(config, level)

            # load template files
            self._load_templates(config)

            # loading the auth configuration
            self._init_auth(config)

            # Loading the attributes
            self.attributes_file = \
                self._get_param('attributes', 'attributes.file', config)
            cherrypy.log.error(
                msg="loading attributes file '%(file)s'" %
                    {'file': self.attributes_file},
                severity=logging.DEBUG
            )

            self.attributes = Attributes(self.attributes_file)

            cherrypy.log.error(
                msg="init directories backends",
                severity=logging.DEBUG
            )
            self._init_backends(config)
            self._check_backends()

            # loading the ppolicy
            self._init_ppolicy(config)

            cherrypy.log.error(
                msg="application started",
                severity=logging.INFO
            )

        except Exception as e:
            self._handle_exception(e)
            cherrypy.log.error(
                msg="application failed to start",
                severity=logging.ERROR
            )
            exit(1)

    def _search(self, searchstring):
        """ search users
        @str searchstring: search string
        @rtype: dict, {<user>: {<attr>: <value>}}
        """
        if searchstring is None:
            return {}
        ret = {}
        for b in self.backends:
            tmp = self.backends[b].search(searchstring)
            for u in tmp:
                if u not in ret:
                    ret[u] = {}
                for attr in tmp[u]:
                    if attr in self.attributes.backend_attributes[b]:
                        attrid = self.attributes.backend_attributes[b][attr]
                        if attr not in ret[u]:
                            ret[u][attrid] = tmp[u][attr]
        return ret

    def _get_user(self, username):
        """ get user attributes
        @str username: user to get
        @rtype: dict, {<attr>: <value>}
        """
        if username is None:
            return {}
        ret = {}
        for b in self.backends:
            tmp = self.backends[b].get_user(username)
            for attr in tmp:
                if attr in self.attributes.backend_attributes[b]:
                    attrid = self.attributes.backend_attributes[b][attr]
                    if attr not in ret:
                        ret[attrid] = tmp[attr]

        cherrypy.log.error(
            msg="user '" + username + "' attributes " + str(ret),
            severity=logging.DEBUG
        )
        return ret

    def _parse_params(self, params):
        """ get user attributes
        @dict params: form parameters
        @rtype: dict, {<type>: {<attr>: <value>}}
        """
        ret = {'attrs': {}, 'roles': {}, 'groups': {}}
        for p in params:
            # each form attributes is prefixed with type, ex: attr.uidNumber
            # separate this prefix from the attribute name
            p_type, sep, param = p.partition('.')
            if p_type == 'attr':
                ret['attrs'][param] = params[p]
            elif p_type == 'role':
                ret['roles'][param] = params[p]
            elif p_type == 'group':
                # with groups there is a second prefix
                # corresponding to the backend
                backend, sep, value = param.partition('.')
                if backend not in ret['groups']:
                    ret['groups'][backend] = []
                ret['groups'][backend].append(value)
        return ret

    def _check_admin(self):
        """ check in the session database if current user
        is an ldapcherry administrator
        @rtype: boolean, True if administrator, False otherwise
        """
        if self.auth_mode == 'none':
            return True
        return cherrypy.session['isadmin']

    def _check_auth(self, must_admin):
        """ check if a user is autheticated and, optionnaly an administrator
        if user not authentifaced -> redirection to login page (with base64
            of the originaly requested page (redirection after login)
        if user authenticated, not admin and must_admin enabled -> 403 error
        @boolean must_admin: flag "user must be an administrator to access
            this page"
        @rtype str: login of the user
        """
        if self.auth_mode == 'none':
            return 'anonymous'
        username = cherrypy.session.get(SESSION_KEY)

        if cherrypy.request.query_string == '':
            qs = ''
        else:
            qs = '?' + cherrypy.request.query_string
        # base64 of the requested URL
        b64requrl = base64.b64encode(cherrypy.url() + qs)
        if not username:
            # return to login page (with base64 of the url in query string
            raise cherrypy.HTTPRedirect(
                "/signin?url=%(url)s" % {'url': b64requrl},
                )

        if 'connected' not in cherrypy.session \
                or not cherrypy.session['connected']:
            raise cherrypy.HTTPRedirect(
                "/signin?url=%(url)s" % {'url': b64requrl},
                )
        if cherrypy.session['connected'] and \
                not cherrypy.session['isadmin']:
            if must_admin:
                # user is not an administrator, so he gets 403 Forbidden
                raise cherrypy.HTTPError(
                    "403 Forbidden",
                    "You are not allowed to access this resource.",
                    )
            else:
                return username
        if cherrypy.session['connected'] and \
                cherrypy.session['isadmin']:
            return username
        else:
            raise cherrypy.HTTPRedirect(
                "/signin?url=%(url)s" % {'url': b64requrl},
                )

    def _adduser(self, params):
        cherrypy.log.error(
            msg="add user form attributes: " + str(params),
            severity=logging.DEBUG
        )
        badd = {}

        for attr in self.attributes.get_attributes():
            if self.attributes.attributes[attr]['type'] == 'password':
                pwd1 = attr + '1'
                pwd2 = attr + '2'
                if params['attrs'][pwd1] != params['attrs'][pwd2]:
                    raise Exception()
                params['attrs'][attr] = params['attrs'][pwd1]
            if attr in params['attrs']:
                backends = self.attributes.get_backends_attributes(attr)
                for b in backends:
                    if b not in badd:
                        badd[b] = {}
                    badd[b][backends[b]] = params['attrs'][attr]
        for b in badd:
            self.backends[b].add_user(badd[b])

        key = self.attributes.get_key()
        username = params['attrs'][key]
        sess = cherrypy.session
        admin = str(sess.get(SESSION_KEY, None))

        cherrypy.log.error(
            msg="user '" + username + "' added by '" + admin + "'",
            severity=logging.INFO
        )
        cherrypy.log.error(
            msg="user '" + username + "' attributes: " + str(badd),
            severity=logging.DEBUG
        )

        roles = []
        for r in self.roles.get_allroles():
            if r in params['roles']:
                roles.append(r)
        groups = self.roles.get_groups(roles)
        for b in groups:
            self.backends[b].add_to_groups(username, Set(groups[b]))

        cherrypy.log.error(
            msg="user '" + username + "' made member of " +
                str(roles) + " by '" + admin + "'",
            severity=logging.INFO
        )
        cherrypy.log.error(
            msg="user '" + username + "' groups: " + str(groups),
            severity=logging.DEBUG
        )

    def _modify_attrs(self, params, attr_list, username):
        badd = {}
        for attr in attr_list:
            if self.attributes.attributes[attr]['type'] == 'password':
                pwd1 = attr + '1'
                pwd2 = attr + '2'
                if pwd1 in params['attrs']:
                    if params['attrs'][pwd1] != params['attrs'][pwd2]:
                        raise Exception()
                    params['attrs'][attr] = params['attrs'][pwd1]
            if attr in params['attrs']:
                backends = self.attributes.get_backends_attributes(attr)
                for b in backends:
                    if b not in badd:
                        badd[b] = {}
                    if params['attrs'][attr] != '':
                        badd[b][backends[b]] = params['attrs'][attr]
        for b in badd:
            self.backends[b].set_attrs(username, badd[b])
        return badd

    def _selfmodify(self, params):
        cherrypy.log.error(
            msg="modify user form attributes: " + str(params),
            severity=logging.DEBUG
        )
        sess = cherrypy.session
        username = str(sess.get(SESSION_KEY, None))
        badd = self._modify_attrs(
            params,
            self.attributes.get_selfattributes(),
            username,
            )
        cherrypy.log.error(
            msg="user '" + username + "' modified his attributes",
            severity=logging.INFO
        )
        cherrypy.log.error(
            msg="user '" + username + "' attributes: " + str(badd),
            severity=logging.DEBUG
        )

    def _modify(self, params):
        cherrypy.log.error(
            msg="modify user form attributes: " + str(params),
            severity=logging.DEBUG
        )
        key = self.attributes.get_key()
        username = params['attrs'][key]

        badd = self._modify_attrs(
            params,
            self.attributes.get_attributes(),
            username
            )

        sess = cherrypy.session
        admin = str(sess.get(SESSION_KEY, None))

        cherrypy.log.error(
            msg="user '" + username + "' modified by '" + admin + "'",
            severity=logging.INFO
        )
        cherrypy.log.error(
            msg="user '" + username + "' attributes: " + str(badd),
            severity=logging.DEBUG
        )

        tmp = self._get_roles(username)
        roles_current = tmp['roles']
        lonely_groups = tmp['unusedgroups']
        roles_member = []
        roles_not_member = []

        groups_keep = {}
        groups_remove = {}

        for b in lonely_groups:
            for g in lonely_groups[b]:
                if b in params['groups'] and g in params['groups'][b]:
                    if b not in groups_keep:
                        groups_keep[b] = []
                    groups_keep[b].append(g)

                else:
                    if b not in groups_remove:
                        groups_remove[b] = []
                    groups_remove[b].append(g)

        for r in self.roles.get_allroles():
            if r in params['roles']:
                roles_member.append(r)
            else:
                roles_not_member.append(r)

        groups_current = self.roles.get_groups(roles_current)
        groups_rm = self.roles.get_groups(roles_not_member)
        groups_add = self.roles.get_groups(roles_member)

        for b in groups_add:
            for g in [groups_add, groups_keep,
                      groups_current, lonely_groups]:
                if b not in g:
                    g[b] = []
            tmp = \
                Set(groups_add[b]) - \
                Set(groups_keep[b]) - \
                Set(groups_current[b]) - \
                Set(lonely_groups[b])
            cherrypy.log.error(
                msg="user '" + username + "' added to groups: " +
                    str(list(tmp)) + " in backend '" + b + "'",
                severity=logging.DEBUG
            )
            self.backends[b].add_to_groups(username, tmp)
        for b in groups_rm:
            for g in [groups_remove, groups_rm, groups_add,
                      groups_keep, groups_current, lonely_groups]:
                if b not in g:
                    g[b] = []
            tmp = \
                (
                    (Set(groups_rm[b]) | Set(groups_remove[b])) -
                    (Set(groups_keep[b]) | Set(groups_add[b]))
                ) & \
                (
                    Set(groups_current[b]) | Set(lonely_groups[b])
                )
            cherrypy.log.error(
                msg="user '" + username + "' removed from groups: " +
                    str(list(tmp)) + " in backend '" + b + "'",
                severity=logging.DEBUG
            )
            self.backends[b].del_from_groups(username, tmp)

        cherrypy.log.error(
            msg="user '" + username + "' made member of " +
                str(roles_member) + " by '" + admin + "'",
            severity=logging.INFO
        )

    def _deleteuser(self, username):
        for b in self.backends:
            self.backends[b].del_user(username)
            cherrypy.log.error(
                msg="user '" + username + "' deleted from backend '" + b + "'",
                severity=logging.DEBUG
            )

        cherrypy.log.error(
            msg="User '" + username + "' deleted",
            severity=logging.INFO
        )

    def _checkppolicy(self, password):
        ret = self.ppolicy.check(password)
        return ret

    @cherrypy.expose
    def signin(self, url=None):
        """simple signin page
        """
        return self.temp_login.render(url=url)

    @cherrypy.expose
    def login(self, login, password, url=None):
        """login page
        """
        auth = self._auth(login, password)
        cherrypy.session['isadmin'] = auth['isadmin']
        cherrypy.session['connected'] = auth['connected']

        if auth['connected']:
            if auth['isadmin']:
                message = \
                    "login success for user '%(user)s' as administrator" % {
                        'user': login
                    }
            else:
                message = \
                    "login success for user '%(user)s' as normal user" % {
                        'user': login
                    }
            cherrypy.log.error(
                msg=message,
                severity=logging.INFO
            )
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = login
            if url is None:
                redirect = "/"
            else:
                redirect = base64.b64decode(url)
            raise cherrypy.HTTPRedirect(redirect)
        else:
            message = "login failed for user '%(user)s'" % {
                'user': login
            }
            cherrypy.log.error(
                msg=message,
                severity=logging.WARNING
            )
            if url is None:
                qs = ''
            else:
                qs = '?url=' + url
            raise cherrypy.HTTPRedirect("/signin" + qs)

    @cherrypy.expose
    def logout(self):
        """ logout page
        """
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None

        cherrypy.log.error(
            msg="user '%(user)s' logout" % {'user': username},
            severity=logging.INFO
        )
        raise cherrypy.HTTPRedirect("/signin")

    @cherrypy.expose
    def index(self):
        """main page rendering
        """
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        return self.temp_index.render(is_admin=is_admin)

    @cherrypy.expose
    def searchuser(self, searchstring=None):
        """ search user page """
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        if searchstring is not None:
            res = self._search(searchstring)
        else:
            res = None
        attrs_list = self.attributes.get_search_attributes()
        return self.temp_searchuser.render(
            searchresult=res,
            attrs_list=attrs_list,
            is_admin=is_admin
            )

    @cherrypy.expose
    def checkppolicy(self, **params):
        """ search user page """
        keys = params.keys()
        if len(keys) != 1:
            cherrypy.response.status = 403
            return "bad argument"
        password = params[keys[0]]
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        ret = self._checkppolicy(password)
        if ret['match']:
            cherrypy.response.status = 200
        else:
            cherrypy.response.status = 400
        return json.dumps(ret, separators=(',', ':'))

    @cherrypy.expose
    def searchadmin(self, searchstring=None):
        """ search user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()
        if searchstring is not None:
            res = self._search(searchstring)
        else:
            res = None
        attrs_list = self.attributes.get_search_attributes()
        return self.temp_searchadmin.render(
            searchresult=res,
            attrs_list=attrs_list,
            is_admin=is_admin
            )

    @cherrypy.expose
    def adduser(self, **params):
        """ add user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()

        if cherrypy.request.method.upper() == 'POST':
            notification = "<script type=\"text/javascript\">" \
                "$.notify('User Added')" \
                "</script>"
            params = self._parse_params(params)
            self._adduser(params)
        else:
            notification = ''

        graph = {}
        for r in self.roles.graph:
            s = list(self.roles.graph[r]['sub_roles'])
            p = list(self.roles.graph[r]['parent_roles'])
            graph[r] = {'sub_roles': s, 'parent_roles': p}
        graph_js = json.dumps(graph, separators=(',', ':'))
        display_names = {}
        for r in self.roles.flatten:
            display_names[r] = self.roles.flatten[r]['display_name']
        roles_js = json.dumps(display_names, separators=(',', ':'))
        form = self.temp_form.render(
            attributes=self.attributes.attributes,
            values=None,
            modify=False,
            autofill=True
            )
        roles = self.temp_roles.render(
            roles=self.roles.flatten,
            graph=self.roles.graph,
            graph_js=graph_js,
            roles_js=roles_js,
            current_roles=None
            )
        return self.temp_adduser.render(
            form=form,
            roles=roles,
            is_admin=is_admin,
            notification=notification
            )

    @cherrypy.expose
    def delete(self, user):
        """ remove user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()
        referer = cherrypy.request.headers['Referer']
        self._deleteuser(user)
        raise cherrypy.HTTPRedirect(referer)

    @cherrypy.expose
    def modify(self, user=None, **params):
        """ modify user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()

        if cherrypy.request.method.upper() == 'POST':
            notification = "<script type=\"text/javascript\">" \
                "$.notify('User Modify')" \
                "</script>"
            params = self._parse_params(params)
            self._modify(params)
            referer = cherrypy.request.headers['Referer']
            raise cherrypy.HTTPRedirect(referer)
        else:
            notification = ''

        graph = {}
        for r in self.roles.graph:
            s = list(self.roles.graph[r]['sub_roles'])
            p = list(self.roles.graph[r]['parent_roles'])
            graph[r] = {'sub_roles': s, 'parent_roles': p}
        graph_js = json.dumps(graph, separators=(',', ':'))
        display_names = {}
        for r in self.roles.flatten:
            display_names[r] = self.roles.flatten[r]['display_name']
        user_attrs = self._get_user(user)
        tmp = self._get_roles(user)
        user_roles = tmp['roles']
        user_lonely_groups = tmp['unusedgroups']
        roles_js = json.dumps(display_names, separators=(',', ':'))
        key = self.attributes.get_key()
        form = self.temp_form.render(
            attributes=self.attributes.attributes,
            values=user_attrs,
            modify=True,
            keyattr=key,
            autofill=False
            )
        roles = self.temp_roles.render(
            roles=self.roles.flatten,
            graph=self.roles.graph,
            graph_js=graph_js,
            roles_js=roles_js,
            current_roles=user_roles
            )
        return self.temp_modify.render(
            form=form,
            roles=roles,
            is_admin=is_admin,
            notification=notification,
            standalone_groups=user_lonely_groups
            )

    @cherrypy.expose
    def selfmodify(self, **params):
        """ self modify user page """
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        sess = cherrypy.session
        user = str(sess.get(SESSION_KEY, None))
        if self.auth_mode == 'none':
            return self.temp_error.render(
                is_admin=is_admin,
                alert='warning',
                message="Not accessible with authentication disabled."
                )
        if cherrypy.request.method.upper() == 'POST':
            params = self._parse_params(params)
            self._selfmodify(params)
        user_attrs = self._get_user(user)
        form = self.temp_form.render(
            attributes=self.attributes.get_selfattributes(),
            values=user_attrs,
            modify=True,
            autofill=False
            )
        return self.temp_selfmodify.render(form=form, is_admin=is_admin)
