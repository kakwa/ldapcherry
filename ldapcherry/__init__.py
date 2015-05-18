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
            # preload templates
            self.temp_lookup = lookup.TemplateLookup(
                    directories=self.template_dir, input_encoding='utf-8'
                    )
            self.temp_index = self.temp_lookup.get_template('index.tmpl')
            self.temp_error = self.temp_lookup.get_template('error.tmpl')
            self.temp_login = self.temp_lookup.get_template('login.tmpl')

            # loading the authentification module
            #auth_module = self._get_param('auth', 'auth.module', config)
            #auth = __import__(auth_module, globals(), locals(), ['Auth'], -1)
            #self.auth = auth.Auth(config['auth'], cherrypy.log)

        except Exception as e:
            self._handle_exception(e)
            exit(1)
            
    def _get_loglevel(self, level):
        """ return logging level object
        corresponding to a given level passed as
        a string
        """
        if level == 'debug':
            return logging.DEBUG
        elif level == 'notice':
            return logging.NOTICE
        elif level == 'info':
            return logging.INFO
        elif level == 'warning' or level == 'warn':
            return logging.WARNING
        elif level == 'error' or level == 'err':
            return logging.ERROR
        elif level == 'critical' or level == 'crit':
            return logging.CRITICAL
        elif level == 'alert':
            return logging.ALERT
        elif level == 'emergency' or level == 'emerg':
            return logging.EMERGENCY
        else:
            return logging.INFO

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

    @cherrypy.expose
    def signin(self):
        """simple signin page
        """
        return self.temp_login.render()

    @cherrypy.expose
    def login(self, login, password):
        """login page
        """
        if self.auth.check_credentials(login, password):
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
        user = self.auth.end_session()
        message = "user '%(user)s' logout" % {
            'user': user
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
        pass

    @cherrypy.expose
    def searchuser(self):
        """ search user page """
        pass

    @cherrypy.expose
    def adduser(self):
        """ add user page """
        pass

    @cherrypy.expose
    def removeuser(self):
        """ remove user page """
        pass

    @cherrypy.expose
    def modifyuser(self):
        """ modify user page """
        pass

    @cherrypy.expose
    def modifyself(self):
        """ self modify user page """
        pass
