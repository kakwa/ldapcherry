#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# ldapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

#generic imports
import sys
import re
import traceback
import logging
import logging.handlers
from operator import itemgetter
from socket import error as socket_error

from exceptions import *
from ldapcherry.roles import Roles
from ldapcherry.attributes import Attributes

#cherrypy http framework imports
import cherrypy
from cherrypy.lib.httputil import parse_query_string

#mako template engines imports
from mako.template import Template
from mako import lookup

SESSION_KEY = '_cp_username'

# Custom log function to overrige weird error.log function
# of cherrypy
def syslog_error(msg='', context='', 
        severity=logging.INFO, traceback=False):
    if traceback:
        msg += cherrypy._cperror.format_exc()
    if context == '':
        cherrypy.log.error_log.log(severity, msg)
    else:
        cherrypy.log.error_log.log(severity, 
                ' '.join((context, msg)))

class LdapCherry(object):

    def _handle_exception(self, e):
        if hasattr(e, 'log'):
            cherrypy.log.error(
                msg = e.log,
                severity = logging.ERROR
            )
        else:
            cherrypy.log.error(
                msg = "Unkwon exception <%(e)s>" % { 'e' : str(e) },
                severity = logging.ERROR
            )
        # log the traceback as 'debug'
        cherrypy.log.error(
                msg = '',
                severity = logging.DEBUG,
                traceback= True
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
        if not default is None:
            return default
        else:
            raise MissingParameter(section, key)


    def _get_groups(self, username):
        ret = {}
        for b in self.backends:
            ret[b] = self.backends[b].get_groups(username)
        return ret

    def _get_roles(self, username):
        groups = self._get_groups(username)
        return self.roles.get_roles(groups)

    def _is_admin(self, username):
        roles = self._get_roles(username)
        return self.roles.is_admin(roles['roles'])

    def _check_backends(self):
        backends = self.backends_params.keys()
        for b in self.roles.get_backends():
            if not b in backends:
                raise MissingBackend(b)
        for b in self.roles.get_backends():
            if not b in backends:
                raise MissingBackend(b)

    def _init_backends(self, config):
        self.backends_params = {}
        self.backends = {}
        for entry in config['backends']:
            # split at the first dot
            backend, sep, param = entry.partition('.')
            value = config['backends'][entry]
            if not backend in self.backends_params:
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
                self.backends[backend] = bc.Backend(params, cherrypy.log, backend, attrslist)
            except MissingParameter as e:
                raise e
            except:
                raise BackendModuleInitFail(module)


    def _init_auth(self, config):
        self.auth_mode = self._get_param('auth', 'auth.mode', config)
        if self.auth_mode in ['and', 'or', 'none']:
            pass
        elif self.auth_mode == 'custom':
            # load custom auth module
            auth_module = self._get_param('auth', 'auth.module', config)
            auth = __import__(auth_module, globals(), locals(), ['Auth'], -1)
            self.auth = auth.Auth(config['auth'], cherrypy.log)
        else:
            raise WrongParamValue('auth.mode', 'auth', ['and', 'or', 'none', 'custom'])

        self.roles_file = self._get_param('roles', 'roles.file', config)
        cherrypy.log.error(
            msg = "loading roles file <%(file)s>" % { 'file': self.roles_file },
            severity = logging.DEBUG
        )
        self.roles = Roles(self.roles_file)


    def _set_access_log(self, config, level):
        access_handler = self._get_param('global', 'log.access_handler', config, 'syslog')

        # log format for syslog
        syslog_formatter = logging.Formatter(
                "ldapcherry[%(process)d]: %(message)s")

        # replace access log handler by a syslog handler
        if access_handler == 'syslog':
            cherrypy.log.access_log.handlers = []
            handler = logging.handlers.SysLogHandler(address = '/dev/log',
                    facility='user')
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
        error_handler = self._get_param('global', 'log.error_handler', config, 'syslog')

        # log format for syslog
        syslog_formatter = logging.Formatter(
                "ldapcherry[%(process)d]: %(message)s")

        # replacing the error handler by a syslog handler
        if error_handler == 'syslog':
            cherrypy.log.error_log.handlers = []

            # redefining log.error method because cherrypy does weird
            # things like adding the date inside the message 
            # or adding space even if context is empty 
            # (by the way, what's the use of "context"?)
            cherrypy.log.error = syslog_error

            handler = logging.handlers.SysLogHandler(address = '/dev/log',
                    facility='user')
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

    def reload(self, config = None):
        """ load/reload the configuration
        """
        try:
            # log configuration handling
            # get log level 
            # (if not in configuration file, log level is set to debug)
            level = self._get_loglevel(self._get_param('global', 'log.level', config, 'debug'))
            # configure access log
            self._set_access_log(config, level)
            # configure error log
            self._set_error_log(config, level)

            # definition of the template directory
            self.template_dir = self._get_param('resources', 'templates.dir', config)
            cherrypy.log.error(
                msg = "loading templates from dir <%(dir)s>" % { 'dir': self.template_dir },
                severity = logging.DEBUG
            )
            # preload templates
            self.temp_lookup = lookup.TemplateLookup(
                    directories=self.template_dir, input_encoding='utf-8'
                    )
            self.temp_index = self.temp_lookup.get_template('index.tmpl')
            self.temp_error = self.temp_lookup.get_template('error.tmpl')
            self.temp_login = self.temp_lookup.get_template('login.tmpl')


            self._init_auth(config)

            self.attributes_file = self._get_param('attributes', 'attributes.file', config)
            cherrypy.log.error(
                msg = "loading attributes file <%(file)s>" % { 'file': self.attributes_file },
                severity = logging.DEBUG
            )

            self.attributes = Attributes(self.attributes_file)

            cherrypy.log.error(
                msg = "init directories backends",
                severity = logging.DEBUG
            )
            self._init_backends(config)
            self._check_backends()
            cherrypy.log.error(
                msg = "application started",
                severity = logging.INFO
            )

        except Exception as e:
            self._handle_exception(e)
            cherrypy.log.error(
                msg = "application failed to start",
                severity = logging.ERROR
            )
            exit(1)
            
    def _reraise(self, exception):
        """ reraise a given exception"""
        raise exception
    
    def _error_handler(self, exception, backend=''):
        """ exception handling function, takes an exception
        and returns the right error page and emits a log
        """

        # log and error page handling
        def render_error(alert, message):
            if alert == 'danger':
                severity = logging.ERROR
            elif alert == 'warning':
                severity = logging.WARNING
            else:
                severity = logging.CRITICAL

            cherrypy.log.error(
                    msg = message,
                    severity = severity
                    )

            return self.temp_error.render(
                        logout_button = self.auth.logout_button,
                        alert = alert,
                        message = message,
                )

        # reraise the exception
        try:
            self._reraise(exception)

        # error handling
        except ldapcherry.exception.MissingParameter:
            cherrypy.response.status = 500 
            alert = 'danger'
            message = 'Example danger'
            return render_error(alert, message)

        except KeyError:
            cherrypy.response.status = 400
            alert = 'warning'
            message = 'Example warning'
            return render_error(alert, message)

    def _check_auth(self, must_admin):
        if not 'connected' in cherrypy.session or not cherrypy.session['connected']:
            raise cherrypy.HTTPRedirect("/signin")
        if cherrypy.session['connected'] and \
                not cherrypy.session['isadmin']:
            if must_admin:
                raise cherrypy.HTTPError("403 Forbidden", "You are not allowed to access this resource.")
            else:
                return
        if cherrypy.session['connected'] and \
                cherrypy.session['isadmin']:
            return
        else:
            raise cherrypy.HTTPRedirect("/signin")

    @cherrypy.expose
    def signin(self):
        """simple signin page
        """
        return self.temp_login.render()

    @cherrypy.expose
    def login(self, login, password):
        """login page
        """
        auth = self._auth(login, password)
        cherrypy.session['isadmin'] = auth['isadmin']
        cherrypy.session['connected'] = auth['connected']

        if auth['connected']:
            message = "login success for user '%(user)s'" % {
                'user': login
            }
            cherrypy.log.error(
                msg = message,
                severity = logging.INFO
            )
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = login
            raise cherrypy.HTTPRedirect("/")
        else:
            message = "login failed for user '%(user)s'" % {
                'user': login
            }
            cherrypy.log.error(
                msg = message,
                severity = logging.WARNING
            )
            raise cherrypy.HTTPRedirect("/signin")

    @cherrypy.expose
    def logout(self):
        """ logout page 
        """
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None

        message = "user '%(user)s' logout" % {
            'user': username
        }
        cherrypy.log.error(
            msg = message,
            severity = logging.INFO
        )
        raise cherrypy.HTTPRedirect("/signin")

    @cherrypy.expose
    def index(self, **params):
        """main page rendering
        """
        self._check_auth(must_admin=False)
        pass

    @cherrypy.expose
    def searchuser(self):
        """ search user page """
        self._check_auth(must_admin=True)
        pass

    @cherrypy.expose
    def adduser(self):
        """ add user page """
        self._check_auth(must_admin=True)
        pass

    @cherrypy.expose
    def removeuser(self):
        """ remove user page """
        self._check_auth(must_admin=True)
        pass

    @cherrypy.expose
    def modifyuser(self):
        """ modify user page """
        self._check_auth(must_admin=True)
        pass

    @cherrypy.expose
    def modifyself(self):
        """ self modify user page """
        self._check_auth(must_admin=False)
        pass
