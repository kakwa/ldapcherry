#!/usr/bin/env python2

import os
import sys

#
# This script sets up the ldapcherry config files through environment variables that are passed at
# startup time.
#

ldapcherry_ini_settings = {
    'SERVER_SOCKET_HOST': '0.0.0.0',
    'SERVER_SOCKET_PORT': '80',
    'SERVER_THREAD_POOL': '0',
    'LOG_ACCESS_HANDLER': 'stdout',
    'LOG_ERROR_HANDLER': 'stdout',
    'LOG_LEVEL': '',
    'LDAP_DISPLAY_NAME': 'My LDAP Directory',
    'LDAP_URI': '',
    'LDAP_CA': '',
    'LDAP_STARTTLS': '',
    'LDAP_CHECKCERT': '',
    'LDAP_BINDDN': '',
    'LDAP_PASSWORD': '',
    'LDAP_TIMEOUT': '1',
    'LDAP_GROUPDN': 'group',
    'LDAP_USERDN': 'people',
    'LDAP_USER_FILTER_TMPL': '',
    'LDAP_GROUP_FILTER_TMPL': '',
    'LDAP_SEARCH_FILTER_TMPL': '',
    'LDAP_OBJECTCLASSES': '',
    'LDAP_DN_USER_ATTR': '',
    'AD_DISPLAY_NAME': '',
    'AD_DOMAIN': '',
    'AD_LOGIN': '',
    'AD_PASSWORD': '',
    'AD_URI': '',
    'AD_CA': '',
    'AD_STARTTLS': '',
    'AD_CHECKCERT': ''
}

with open('/etc/ldapcherry/ldapcherry.ini', 'r') as file:
    filelines = file.readlines()

for setting in ldapcherry_ini_settings:
    # Replace the instances of the key with the value of the env var or the
    # default
    setting_key = setting.replace('_', '.', 1).lower()
    setting_val = os.getenv(setting, ldapcherry_ini_settings[setting])
    if (any(line.startswith(setting_key) for line in filelines)
            and ldapcherry_ini_settings[setting] != ''):
        # We know that it is defined somewhere, so we don't want to uncomment
        # any of the commented-out lines to replace it
        indeces = [idx for idx, elem in enumerate(filelines)
                   if elem.startswith(setting_key)]
        # Exit if there are more than one instance defined
        if len(indeces) != 1:
            sys.exit()
        filelines[indeces[0]] = "{0} = '{1}'\n".format(setting_key, setting_val)
    elif (any(line.startswith('#' + setting_key) for line in filelines)
            and ldapcherry_ini_settings[setting] != ''):
        # We know that it is defined somewhere, but behind a comment. We will
        # just change the first instance of it to the value that we want.
        # We also know that it isn't defined anywhere due to the earlier test.
        indeces = [idx for idx, elem in enumerate(filelines)
                   if elem.startswith("#" + setting_key)]
        filelines[indeces[0]] = "{0} = '{1}'\n".format(setting_key, setting_val)
    else:
        # It is not defined anywhere
        continue

# Write the file out again
with open('/etc/ldapcherry/ldapcherry.ini', 'w') as file:
    for fileline in filelines:
        file.write("{}".format(fileline))

os.system("/usr/local/bin/ldapcherryd -c /etc/ldapcherry/ldapcherry.ini -D")
