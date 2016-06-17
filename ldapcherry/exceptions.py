# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import string
import cherrypy


class MissingParameter(Exception):
    def __init__(self, section, key):
        self.section = section
        self.key = key
        self.log = \
            "missing parameter '%(key)s' in section '%(section)s'" % \
            {'key': key, 'section': section}


class MissingKey(Exception):
    def __init__(self, key, section, ymlfile):
        self.key = key
        self.section = section
        self.ymlfile = ymlfile
        self.log = \
            "missing key '%(key)s' in section '%(section)s'" \
            " inside file '%(ymlfile)s'" % \
            {'key': key, 'section': section, 'ymlfile': ymlfile}


class DumplicateRoleKey(Exception):
    def __init__(self, role):
        self.role = role
        self.log = \
            "duplicate role key '%(role)s' in role file" % \
            {'role': role}


class MissingRole(Exception):
    def __init__(self, role):
        self.role = role
        self.log = \
            "role '%(role)s' does not exist in role file" % \
            {'role': role}


class MissingBackend(Exception):
    def __init__(self, backend):
        self.backend = backend
        self.log = \
            "backend '%(backend)s' does not exist in main config file" % \
            {'backend': backend}


class WrongBackend(Exception):
    def __init__(self, backend):
        self.backend = backend
        self.log = \
            "backend '%(backend)s' does not exist" % \
            {'backend': backend}


class DumplicateRoleContent(Exception):
    def __init__(self, role1, role2):
        self.role1 = role1
        self.role2 = role2
        self.log = \
            "role '%(role1)s' and '%(role2)s' are identical" % \
            {'role1': role1, 'role2': role2}


class MissingRolesFile(Exception):
    def __init__(self, rolefile):
        self.rolefile = rolefile
        self.log = \
            "fail to open role file '%(rolefile)s'" % \
            {'rolefile': rolefile}


class PasswordMissMatch(Exception):
    def __init__(self):
        self.log = "password missmatch"


class PPolicyError(Exception):
    def __init__(self):
        self.log = "password doesn't match ppolicy"


class MissingMainFile(Exception):
    def __init__(self, config):
        self.rolefile = rolefile
        self.log = \
            "fail to open main file '%(config)s'" % \
            {'rolefile': rolefile}


class MissingAttributesFile(Exception):
    def __init__(self, attributesfile):
        self.attributesfile = attributesfile
        self.log = \
            "fail to open attributes file '%(attributesfile)s'" % \
            {'attributesfile': attributesfile}


class BackendModuleLoadingFail(Exception):
    def __init__(self, module):
        self.module = module
        self.log = \
            "module '%(module)s' not in python path" % \
            {'module': module}


class BackendModuleInitFail(Exception):
    def __init__(self, module):
        self.module = module
        self.log = \
            "fail to init module '%(module)s'" % \
            {'module': module}


class WrongParamValue(Exception):
    def __init__(self, param, section, possible_values):
        self.possible_values = possible_values
        self.section = section
        self.param = param
        possible_values_str = string.join(possible_values, ', ')
        self.log = \
            "wrong value for param '%(param)s' in section '%(section)s'" \
            ", possible values are [%(values)s]" % \
            {
                'param': param,
                'section': section,
                'values': possible_values_str
            }


class DumplicateUserKey(Exception):
    def __init__(self, attrid1, attrid2):
        self.attrid1 = attrid1
        self.attrid2 = attrid2
        self.log = \
            "duplicate key in '%(attrid1)s' and '%(attrid2)s'" % \
            {'attrid1': attrid1, 'attrid2': attrid2}


class MissingUserKey(Exception):
    def __init__(self):
        self.log = "missing key"


class WrongAttributeType(Exception):
    def __init__(self, key, section, ymlfile):
        self.key = key
        self.section = section
        self.ymlfile = ymlfile
        self.log = \
            "wrong attribute type '%(key)s'" \
            " in section '%(section)s'" \
            " inside file '%(ymlfile)s'" % \
            {'key': key, 'section': section, 'ymlfile': ymlfile}


class PasswordAttributesCollision(Exception):
    def __init__(self, key):
        self.key = key
        self.log = \
            "key '" + key + "' type is password," \
            " keys '" + key + "1' and '" + key + "2'" \
            " are reserved and cannot be used"


class WrongAttrValue(Exception):
    def __init__(self, attr, attrtype):
        self.attr = attr
        self.attrtype = attrtype
        self.log = \
            "input for attribute '" + attr + "'" \
            " doesn't match type '" + attrtype + "'"


class AttrNotDefined(Exception):
    def __init__(self, attr):
        self.attr = attr
        self.log = \
            "attribute '" + attr + "' is not defined in configuration"


class UserDoesntExist(Exception):
    def __init__(self, user, backend):
        self.user = user
        self.bakend = backend
        self.log = \
            "user '" + user + "'" \
            " does not exist" \
            " in backend '" + backend + "'"


class UserAlreadyExists(Exception):
    def __init__(self, user, backend):
        self.user = user
        self.bakend = backend
        self.log = \
            "user '" + user + "'" \
            " already exists" \
            " in backend '" + backend + "'"


class GroupDoesntExist(Exception):
    def __init__(self, group, backend):
        self.group = group
        self.bakend = backend
        self.log = \
            "group '" + group + "'" \
            " does not exist" \
            " in backend '" + backend + "'"


def exception_decorator(func):
    def ret(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except cherrypy.HTTPRedirect as e:
            raise e
        except cherrypy.HTTPError as e:
            raise e
        except Exception as e:
            cherrypy.response.status = 500
            self._handle_exception(e)
            username = self._check_session()
            if not username:
                return self.temp['service_unavailable.tmpl'].render()
            is_admin = self._check_admin()
            et = type(e)
            if et is UserDoesntExist:
                user = e.user
                return self.temp['error.tmpl'].render(
                    is_admin=is_admin,
                    alert='danger',
                    message="User '" + user + "' does not exist"
                    )
            elif et is UserAlreadyExists:
                user = e.user
                cherrypy.response.status = 400
                return self.temp['error.tmpl'].render(
                    is_admin=is_admin,
                    alert='warning',
                    message="User '" + user + "' already exist"
                    )
            elif et is GroupDoesntExist:
                group = e.group
                return self.temp['error.tmpl'].render(
                    is_admin=is_admin,
                    alert='danger',
                    message="Missing group, please check logs for details"
                    )
            else:
                return self.temp['error.tmpl'].render(
                    is_admin=is_admin,
                    alert='danger',
                    message="An error occured, please check logs for details"
                    )
    return ret
