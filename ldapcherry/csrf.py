# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

"""
Utility functions to generate and verify CSRF tokens.

For details about CSRF attack and protection, see:
* https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)
* https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md
"""

import cherrypy
import secrets
from ldapcherry.exceptions import MissingCSRFParam, \
    MissingCSRFCookie, InvalidCSRFToken


# Names of the different parameters (cookie, post parameter, session variable)
CSRF_COOKIE_NAME = "csrf_reference"
CSRF_INPUT_NAME = "csrf_token"
CSRF_SESSION_NAME = "csrf_token"


def get_csrf_cookie():
    """
    Quick utility function to read CSRF cookie value.

    Return None if the cookie is not present.
    """
    if CSRF_COOKIE_NAME in cherrypy.request.cookie:
        return cherrypy.request.cookie[CSRF_COOKIE_NAME].value
    else:
        return None


def set_csrf_cookie(value):
    """
    Quick utility function to set CSRF cookie value.

    Use cherrypy to set the correct header.
    """
    cherrypy.response.cookie[CSRF_COOKIE_NAME] = value


def generate_token(nb_bytes=32):
    """
    Generate and return a random CSRF token.

    Strong entropy generator from `secrets` library is used to ensure
    the token is not guessable and return value is encoded in hex format.
    @integer nb_bytes can be specified to set the number of bytes
    (each byte resulting in two hex digits)
    """
    return secrets.token_hex(nb_bytes)


def get_csrf_token():
    """
    Return the CSRF token associated with the user.

    Return the CSRF token from session if it exists.
    Else, generate a new one and store it (in session + cookie).
    """
    if CSRF_SESSION_NAME not in cherrypy.session:
        token = generate_token()
        cherrypy.session[CSRF_SESSION_NAME] = token
        set_csrf_cookie(token)
    return cherrypy.session[CSRF_SESSION_NAME]


def get_csrf_field():
    """
    Return an hidden form field containing the CSRF token.

    Return format is a plain string which can be inserted in a template.
    The token is generated and saved if needed (via get_csrf_token() call).
    """
    template = "<input type=\"hidden\" name=\"{name}\" value=\"{value}\"/>"
    return template.format(name=CSRF_INPUT_NAME, value=get_csrf_token())


def ensure_valid_token(**params):
    """
    Ensure request is legitimate by comparing cookie and post parameter.

    Raise an exception if CSRF cookie value is different from CSRF
    post parameter value or if one of them is missing.
    In this case, the request MUST NOT be processed (it is not genuine).
    """
    if CSRF_INPUT_NAME not in params:
        raise MissingCSRFParam()
    if CSRF_COOKIE_NAME not in cherrypy.request.cookie:
        raise MissingCSRFCookie()
    if params.get(CSRF_INPUT_NAME) != get_csrf_cookie():
        raise InvalidCSRFToken()


def validate_csrf(func):
    """
    Decorator ensuring CSRF token is validated before executing request.

    WARNING: only POST requests are checked, for GET requests, you need to call
    ensure_valid_token() manually.
    """
    def ret(self, *args, **kwargs):
        if cherrypy.request.method.upper() == 'POST':
            ensure_valid_token(**kwargs)
            kwargs.pop(CSRF_INPUT_NAME)
        return func(self, *args, **kwargs)
    return ret
