#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# ldapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

# Generic imports
import sys
import traceback
import logging
import logging.handlers
import cherrypy


# Custom log function to override weird error.log function
# of cherrypy
def syslog_error(
        msg='',
        context='',
        severity=logging.INFO,
        traceback=False
        ):

    if traceback and msg == '':
        msg = 'Python Exception:'
    if context == '':
        cherrypy.log.error_log.log(severity, msg)
    else:
        cherrypy.log.error_log.log(
            severity,
            ' '.join((context, msg))
            )
    if traceback:
        import traceback
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


def get_loglevel(level):
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
