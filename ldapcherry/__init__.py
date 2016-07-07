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
from ldapcherry.lclogging import *
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


class LdapCherry(object):

    def _handle_exception(self, e):
        if hasattr(e, 'log'):
            cherrypy.log.error(
                msg=e.log,
                severity=logging.ERROR
            )
        else:
            cherrypy.log.error(
                msg="uncaught exception: [%(e)s]" % {'e': str(e)},
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
        self.backends_display_names = {}
        for entry in config['backends']:
            # split at the first dot
            backend, sep, param = entry.partition('.')
            value = config['backends'][entry]
            if backend not in self.backends_params:
                self.backends_params[backend] = {}
            self.backends_params[backend][param] = value
        for backend in self.backends_params:
            # get the backend display_name
            try:
                self.backends_display_names[backend] = \
                    self.backends_params[backend]['display_name']
            except:
                self.backends_display_names[backend] = backend
                self.backends_params[backend]['display_name'] = backend
            params = self.backends_params[backend]
            # Loading the backend module
            try:
                module = params['module']
            except Exception as e:
                raise MissingParameter('backends', backend + '.module')
            try:
                bc = __import__(module, globals(), locals(), ['Backend'], -1)
            except Exception as e:
                self._handle_exception(e)
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
                raise
            except Exception as e:
                self._handle_exception(e)
                raise BackendModuleInitFail(module)

    def _init_custom_js(self, config):
        self.custom_js = []
        if '/custom' not in config:
            return
        directory = self._get_param(
            '/custom',
            'tools.staticdir.dir',
            config,
            )
        for file in os.listdir(directory):
            if file.endswith(".js"):
                self.custom_js.append(file)

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

    def _set_error_log(self, config, level, debug=False):
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

        if debug:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.DEBUG)
            cherrypy.log.error_log.addHandler(handler)
            cherrypy.log.error_log.setLevel(logging.DEBUG)

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
        # load each template
        self.temp = {}
        for t in ('index.tmpl', 'error.tmpl', 'login.tmpl', '404.tmpl',
                  'searchadmin.tmpl', 'searchuser.tmpl', 'adduser.tmpl',
                  'roles.tmpl', 'groups.tmpl', 'form.tmpl', 'selfmodify.tmpl',
                  'modify.tmpl', 'service_unavailable.tmpl'
                  ):
            self.temp[t] = self.temp_lookup.get_template(t)

    def reload(self, config=None, debug=False):
        """ load/reload configuration
        @dict: configuration of ldapcherry
        """
        try:
            # log configuration handling
            # get log level
            # (if not in configuration file, log level is set to debug)
            level = get_loglevel(
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
            self._set_error_log(config, level, debug)

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

            self.notifications = {}

            self.attributes = Attributes(self.attributes_file)

            cherrypy.log.error(
                msg="init directories backends",
                severity=logging.DEBUG
            )
            self._init_backends(config)
            self._check_backends()

            # loading the ppolicy
            self._init_ppolicy(config)

            # loading custom javascript
            self._init_custom_js(config)

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

    def _add_notification(self, message):
        """ add a notification in the notification queue of a user
        """
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        if username not in self.notifications:
            self.notifications[username] = []
        self.notifications[username].append(message)

    def _empty_notification(self):
        """ empty and return list of message notification
        """
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        if username in self.notifications:
            ret = self.notifications[username]
        else:
            ret = []
        self.notifications[username] = []
        return ret

    def _merge_user_attrs(self, attrs_backend, attrs_out, backend_name):
        """ merge attributes from one backend search to the attributes dict
        output

        """
        for attr in attrs_backend:
            if attr in self.attributes.backend_attributes[backend_name]:
                attrid = self.attributes.backend_attributes[backend_name][attr]
                if attrid not in attrs_out:
                    attrs_out[attrid] = attrs_backend[attr]

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
                self._merge_user_attrs(tmp[u], ret[u], b)
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
            try:
                tmp = self.backends[b].get_user(username)
            except UserDoesntExist as e:
                self._handle_exception(e)
                tmp = {}
            self._merge_user_attrs(tmp, ret, b)

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

    def _check_session(self):
        if self.auth_mode == 'none':
            return 'anonymous'
        return cherrypy.session.get(SESSION_KEY)

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
        username = self._check_session()

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
                    raise PasswordMissMatch()
                if not self._checkppolicy(params['attrs'][pwd1])['match']:
                    raise PPolicyError()
                params['attrs'][attr] = params['attrs'][pwd1]
            if attr in params['attrs']:
                self.attributes.check_attr(attr, params['attrs'][attr])
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
                        raise PasswordMissMatch()
                    if params['attrs'][pwd1] != '' and \
                            not self._checkppolicy(
                                params['attrs'][pwd1]
                                )['match']:
                        raise PPolicyError()
                    params['attrs'][attr] = params['attrs'][pwd1]
            if attr in params['attrs'] and params['attrs'][attr] != '':
                self.attributes.check_attr(attr, params['attrs'][attr])
                backends = self.attributes.get_backends_attributes(attr)
                for b in backends:
                    if b not in badd:
                        badd[b] = {}
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
        sess = cherrypy.session
        admin = str(sess.get(SESSION_KEY, None))

        for b in self.backends:
            self.backends[b].del_user(username)
            cherrypy.log.error(
                msg="user '" + username + "' deleted from backend '" + b + "'",
                severity=logging.DEBUG
            )

        cherrypy.log.error(
            msg="User '" + username + "' deleted by '" + admin + "'",
            severity=logging.INFO
        )

    def _checkppolicy(self, password):
        return self.ppolicy.check(password)

    @cherrypy.expose
    @exception_decorator
    def signin(self, url=None):
        """simple signin page
        """
        return self.temp['login.tmpl'].render(url=url)

    @cherrypy.expose
    @exception_decorator
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
    @exception_decorator
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
    @exception_decorator
    def index(self):
        """main page rendering
        """
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        sess = cherrypy.session
        user = str(sess.get(SESSION_KEY, None))
        if self.auth_mode == 'none':
            user_attrs = None
        else:
            user_attrs = self._get_user(user)
        attrs_list = self.attributes.get_search_attributes()
        print attrs_list
        print user_attrs
        return self.temp['index.tmpl'].render(
            is_admin=is_admin,
            attrs_list=attrs_list,
            searchresult=user_attrs,
            notifications=self._empty_notification(),
            )

    @cherrypy.expose
    @exception_decorator
    def searchuser(self, searchstring=None):
        """ search user page """
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        if searchstring is not None and len(searchstring) > 2:
            res = self._search(searchstring)
        else:
            res = None
        attrs_list = self.attributes.get_search_attributes()
        return self.temp['searchuser.tmpl'].render(
            searchresult=res,
            attrs_list=attrs_list,
            is_admin=is_admin,
            custom_js=self.custom_js,
            notifications=self._empty_notification(),
            )

    @cherrypy.expose
    @exception_decorator
    def checkppolicy(self, **params):
        """ search user page """
        self._check_auth(must_admin=False)
        keys = params.keys()
        if len(keys) != 1:
            cherrypy.response.status = 400
            return "bad argument"
        password = params[keys[0]]
        is_admin = self._check_admin()
        ret = self._checkppolicy(password)
        if ret['match']:
            cherrypy.response.status = 200
        else:
            cherrypy.response.status = 200
        return json.dumps(ret, separators=(',', ':'))

    @cherrypy.expose
    @exception_decorator
    def searchadmin(self, searchstring=None):
        """ search user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()
        if searchstring is not None and len(searchstring) > 2:
            res = self._search(searchstring)
        else:
            res = None
        attrs_list = self.attributes.get_search_attributes()
        return self.temp['searchadmin.tmpl'].render(
            searchresult=res,
            attrs_list=attrs_list,
            is_admin=is_admin,
            custom_js=self.custom_js,
            notifications=self._empty_notification(),
            )

    @cherrypy.expose
    @exception_decorator
    def adduser(self, **params):
        """ add user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()

        if cherrypy.request.method.upper() == 'POST':
            params = self._parse_params(params)
            self._adduser(params)
            self._add_notification("User added")

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
        form = self.temp['form.tmpl'].render(
            attributes=self.attributes.attributes,
            values=None,
            modify=False,
            autofill=True
            )
        roles = self.temp['roles.tmpl'].render(
            roles=self.roles.flatten,
            graph=self.roles.graph,
            graph_js=graph_js,
            roles_js=roles_js,
            current_roles=None,
            )
        return self.temp['adduser.tmpl'].render(
            form=form,
            roles=roles,
            is_admin=is_admin,
            custom_js=self.custom_js,
            notifications=self._empty_notification(),
            )

    @cherrypy.expose
    @exception_decorator
    def delete(self, user):
        """ remove user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()
        try:
            referer = cherrypy.request.headers['Referer']
        except:
            referer = '/'
        self._deleteuser(user)
        self._add_notification('User Deleted')
        raise cherrypy.HTTPRedirect(referer)

    @cherrypy.expose
    @exception_decorator
    def modify(self, user=None, **params):
        """ modify user page """
        self._check_auth(must_admin=True)
        is_admin = self._check_admin()

        if cherrypy.request.method.upper() == 'POST':
            params = self._parse_params(params)
            self._modify(params)
            self._add_notification("User modified")
            try:
                referer = cherrypy.request.headers['Referer']
            except:
                referer = '/'
            raise cherrypy.HTTPRedirect(referer)

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
        if user_attrs == {}:
            cherrypy.response.status = 400
            return self.temp['error.tmpl'].render(
                is_admin=is_admin,
                alert='warning',
                message="User '" + user + "' does not exist"
                )
        tmp = self._get_roles(user)
        user_roles = tmp['roles']
        user_lonely_groups = tmp['unusedgroups']
        roles_js = json.dumps(display_names, separators=(',', ':'))
        key = self.attributes.get_key()
        form = self.temp['form.tmpl'].render(
            attributes=self.attributes.attributes,
            values=user_attrs,
            modify=True,
            keyattr=key,
            autofill=False
            )
        roles = self.temp['roles.tmpl'].render(
            roles=self.roles.flatten,
            graph=self.roles.graph,
            graph_js=graph_js,
            roles_js=roles_js,
            current_roles=user_roles,
            )
        return self.temp['modify.tmpl'].render(
            form=form,
            roles=roles,
            is_admin=is_admin,
            standalone_groups=user_lonely_groups,
            backends_display_names=self.backends_display_names,
            custom_js=self.custom_js,
            notifications=self._empty_notification(),
            )

    @cherrypy.expose
    @exception_decorator
    def default(self, attr=''):
        cherrypy.response.status = 404
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        return self.temp['404.tmpl'].render(
            is_admin=is_admin,
            notifications=self._empty_notification(),
            )

    @cherrypy.expose
    @exception_decorator
    def selfmodify(self, **params):
        """ self modify user page """
        self._check_auth(must_admin=False)
        is_admin = self._check_admin()
        sess = cherrypy.session
        user = str(sess.get(SESSION_KEY, None))
        if self.auth_mode == 'none':
            return self.temp['error.tmpl'].render(
                is_admin=is_admin,
                alert='warning',
                message="Not accessible with authentication disabled."
                )
        if cherrypy.request.method.upper() == 'POST':
            params = self._parse_params(params)
            self._selfmodify(params)
            self._add_notification(
                "Self modification done"
            )
        user_attrs = self._get_user(user)
        if user_attrs == {}:
            return self.temp['error.tmpl'].render(
                is_admin=is_admin,
                alert='warning',
                message="User doesn't exist"
                )
        form = self.temp['form.tmpl'].render(
            attributes=self.attributes.get_selfattributes(),
            values=user_attrs,
            modify=True,
            autofill=False
            )
        return self.temp['selfmodify.tmpl'].render(
            form=form,
            is_admin=is_admin,
            notifications=self._empty_notification(),
            )
