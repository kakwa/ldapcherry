#!/usr/bin/env python2

import os
import re
import ast
import sys
import yaml
import in_place
import itertools
import subprocess
import configparser

#
# This script sets up the ldapcherry config files through environment
# variables that are passed at startup time.
#
# The environment variables are only to be made into upper-case underscore-
# separated versions of the options inside of each section of the
# ldapcherry.ini file. For instance:
#
#   server.socket_host -> SERVER_SOCKET_HOST
#   request.show_tracebacks -> REQUEST_SHOW_TRACEBACKS
#   tools.sessions.timeout -> TOOLS_SESSIONS_TIMEOUT
#   min_length -> MIN_LENGTH
#
# They will be put into their respective sections in the ldapcherry.ini file.
#
# For the yaml configuration files, they are passed as follows:
#
#   shell:
#       description: "Shell of the user"
#       display_name: "Shell"
#       weight: 80
#       values:
#           - /bin/bash
#           - /bin/zsh
#           - /bin/sh
#
#   ATTRIBUTES__SHELL__DESCRIPTION="Shell of the user"
#   ATTRIBUTES__SHELL__DISPLAY_NAME="Shell"
#   ATTRIBUTES__SHELL__WEIGHT="80"
#   ATTRIBUTES__SHELL__VALUES="['/bin/bash', '/bin/zsh', '/bin/sh']"
#

#
# Sane defaults for docker.
#
ldapcherry_default_env_vars = {
    'SERVER_SOCKET_HOST': "'0.0.0.0'",
    'SERVER_SOCKET_PORT': '8080',
    'LOG_ACCESS_HANDLER': "'stdout'",
    'LOG_ERROR_HANDLER': "'stdout'",
}

def exclude_ini_backend(backend, config):
    """
    Remove all options in the ini file associated with the specified backend

    @str backend: the backend to exclude
    @dict config: the configuration
    """
    # Put all of the entries in the backend to exclude into a list in order to
    # avoid removing items from the object that we are iterating over.
    for option in list(config['backends']):
        if option.startswith(backend):
            config.remove_option('backends', option)

    return config


def exclude_yaml_backend(backend, config, conf_file_name):
    """
    Remove all options in the yaml file associated with the specified backend

    @str backend: the backend to exclude
    @dict config: the configuration
    @str conf_file_name: the name of the configuration file
    """
    backends = {'roles': 'backends_groups', 'attributes': 'backends'}
    for top_level in config:
        try:
            config[top_level][backends[conf_file_name]].pop(backend)
        except KeyError:
            continue

    return config


def include_exclude_yaml_backends(config, conf_file_name, possible_backends, used_backends):
    """
    Determine which backends are in play, and implement sane defaults

    @dict config: the configuration
    @str conf_file_name: the name of the configuration file
    @list possible_backends: the backends that can be used
    @list used_backends: the backends that are being used
    """
    if len(used_backends) == 0:
        if conf_file_name == 'roles':
            for role in config:
                demo_bg = config[role]['backends_groups'].pop('ldap')
                config[role]['backends_groups']['demo'] = demo_bg
            config['admin-lv2'].pop('LC_admins')

            #
            # Set up the additional role 'sec-officer'
            #
            config['sec-officer'] = {}
            config['sec-officer']['display_name'] = 'Security Officer'
            config['sec-officer']['description'] = "Security officer"
            config['sec-officer']['LC_admins'] = "True"
            config['sec-officer']['backends_groups'] = {}
            config['sec-officer']['backends_groups']['demo'] = ['SECOFF']

        elif conf_file_name == 'attributes':
            for attr in config:
                attr_backend = config[attr]['backends'].pop('ldap')
                config[attr]['backends']['demo'] = attr_backend

        for backend in possible_backends:
            if backend != 'demo':
                config = exclude_yaml_backend(backend, config, conf_file_name)

    else:
        # Take out all of the backend options that are not in use
        unused_backends = list(set(possible_backends) - set(used_backends))
        for backend in unused_backends:
            config = exclude_yaml_backend(backend, config, conf_file_name)

    return config


def get_backends(all_ini_settings):
    """
    Get both all of the possible backends, and the ones that are actually being
    used

    @dict all_ini_settings: all of the settings possible in the ini file
    """
    # We're going to check the environment variables to see what was passed in.
    # This is assuming that there must be a URI for whichever backend is
    # dynamically passed in. We could parse the config to find out what is
    # defined, but we need to interpret what the container was launched to
    # connect to, which is likely what was passed in via environment vars.
    possible_backends = []

    # Here I _could_ just say possible_backends = ['ldap', 'ad', 'demo'], but
    # I want to make this as low-maintenance as possible. If there is another
    # backend that becomes available, this will catch it as-is.
    for option in all_ini_settings['backends']:
        possible_backend = option.split('.')[0]
        if (possible_backend not in possible_backends and
                possible_backend != 'demo'):
            possible_backends.append(possible_backend)

    # Get all the backends that were passed in with environment vars.
    used_backends = []
    for backend in possible_backends:
        backend_prefix = "{}_".format(backend.upper())
        if any(env_var.startswith(backend_prefix) for env_var in os.environ):
            used_backends.append(backend)

    return possible_backends, used_backends


def include_exclude_ini_backends(config, possible_backends, used_backends,
        all_ini_settings):
    """
    Allow sane defaults to be applied to the intended backend, and remove
    unnecessary defaults from the config to avoid backend errors.

    @dict config: the configuration
    @list possible_backends: the backends that can be used
    @list used_backends: the backends that are being used
    @dict all_ini_settings: all of the settings possible in the ini file
    """
    # Insert all of the demo settings if there were no backends specified
    if len(used_backends) == 0:
        # Add all of the demo settings in there.
        for option in all_ini_settings['backends']:
            if option.startswith('demo') and option not in config['backends']:
                config['backends'][option] = all_ini_settings['backends'][option]

        # Set the admin user's security group to allow for all admin actions
        config['backends']['demo.admin.groups'] = "'SECOFF'"

        # Remove all other options for all other backends
        for backend in possible_backends:
            if backend != 'demo':
                config = exclude_ini_backend(backend, config)

    else:
        # Take out all of the backend options that are not in use
        unused_backends = list(set(possible_backends) - set(used_backends))
        for backend in unused_backends:
            config = exclude_ini_backend(backend, config)

    return config


def get_config_value(env_var):
    """
    Format valid configuration values based on the string that is passed

    @str env_var: the environment var that needs to be formatted
    """
    val = os.getenv(env_var)

    if val is not None:
        if val.isdigit():
            return val
        if val in ['True', 'False']:
            return val
        # Handle when we're not passed variables that are properly quoted
        elif (val.startswith("'") and not val.endswith("'")) or "'" in val:
            return "\"{}\"".format(val)
        elif (val.startswith('"') and not val.endswith('"')) or '"' in val:
            return "'{}'".format(val)
        else:
            return "'{}'".format(val)
    elif env_var in ldapcherry_default_env_vars:
        return ldapcherry_default_env_vars[env_var]
    else:
        # This is most likely a blank string
        return False


def set_yaml_override(env_var, config, env_var_list):
    """
    Recursive function to ensure the creation of the appropriate hierarchy in
    the yaml list.

    @str env_var: the environment var that needs to be formatted
    @dict config: the configuration
    @list env_var_list: the list of all present environment vars
    """

    if env_var_list[0] in config and len(env_var_list) > 1:
        # The key exists, but there is more hierarchy to be traversed
        set_yaml_override(env_var, config[env_var_list[0]], env_var_list[1:])
    elif env_var_list[0] not in config and len(env_var_list) > 1:
        # The key isn't already in the config data structure, so create it as a
        # new dictionary, as there is still more hierarchy to be traversed
        config[env_var_list[0]] = {}
        set_yaml_override(env_var, config[env_var_list[0]], env_var_list[1:])
    else:
        # This is the last key, therefore we should insert the value here.
        if get_config_value(env_var).startswith(('{', '[')):
            config[env_var_list[0]] = ast.literal_eval(get_config_value(env_var))
        # We need to remove the value if it's pass into the container as a zero
        # length string
        elif not os.getenv(env_var):
            config.pop(env_var_list[0])
        else:
            config[env_var_list[0]] = get_config_value(env_var)

    return config


def find_yaml_override(config, env_var):
    """
    Find an environment variable that overrides a setting in a yaml
    configuration file

    @dict config: the configuration
    @str env_var: the environment var that needs to be formatted
    """
    # Split the env_var into a list delineated by double underscores
    env_var_list = env_var.lower().split('__')[1:]

    # Keeping in mind that we can have any type of definitions here that can be
    # typed out at the _root_ level, need to have a recursive function
    config = set_yaml_override(env_var, config, env_var_list)

    return config


def find_ini_override(env_var, config, all_ini_settings):
    """
    Find an environment variable that overrides a setting in a yaml
    configuration file

    @str env_var: the environment var that needs to be formatted
    @dict config: the configuration
    @dict all_ini_settings: all of the settings possible in the ini file
    """
    # Here we split the env_var into a list. We are going to be using
    # env vars that are the same as the objects, but all caps and that
    # have underscores instead of periods, but split at the same
    # places. If we split the option at all of the periods as well as
    # the underscores, and compare that to a similarly split env var
    # that has been lower-cased, we should have an accurate comparison.
    env_var_list = env_var.lower().split('_')

    # Quick fix for otherwise sane defaults, but options that have the
    # incorrect suffix. We want to fix that here.
    if env_var == 'SUFFIX':
        suffix = os.getenv(env_var)
        for section in config.sections():
            for option in config[section]:
                setting = config.get(section, option)
                if 'example' in setting:
                    # We don't have to handle `example.org` here, since:
                    #
                    #   1. It doesn't exist in `ldapcherry.ini`
                    #   2. The suffix of an LDAP hierarchy is always in the
                    #       regular `dc=something,dc=TLD` format. We shouldn't
                    #       confuse users by accepting `example.org` here as
                    #       that is technically not an LDAP suffix, but rather
                    #       a _domain_.
                    new_setting = setting.replace('dc=example,dc=org', suffix)
                    config[section][option] = new_setting
        # We return the config here and end this execution of this function
        # since none of the other settings will be affected by the suffix. Or,
        # if so, the suffix will already be baked into the value of the env var
        # that is being passed.
        return config

    # Compare every setting to the env_var_list by splitting the option at all
    # of the periods as well as the underscores, and compare that to the
    # similarly split env var that has been lower-cased. This should cause us
    # to have an accurate comparison.
    for section in all_ini_settings:
        for setting in all_ini_settings[section]:
            option_list = setting.replace('.', ' ').replace('_', ' ').split()
            if env_var_list == option_list:
                # Remove the value if it's passed as an empty string
                if not get_config_value(env_var):
                    config.remove_option(section, setting)
                else:
                    config[section][setting] = get_config_value(env_var)
                return config

    # Here we haven't found a match against either the existing settings, or
    # the commented-out settings, so we are going to just return the config
    # as-is. This most likely means that we've evaluated an env var that was
    # not meant for this program, but that the system uses in some other
    # capacity.
    return config


def all_yaml_settings(yaml_filepath):
    """
    Uncomment all options in the yaml file

    @str yaml_filepath: the path to the yaml configuration file
    """
    # Uncomment the alternate backends to make the defaults available for
    # later
    with in_place.InPlace(yaml_filepath) as commented_file:
        last_line_was_commented = False
        for line in commented_file:
            # Our rationale here is that we want to catch all of the top-level keys
            # in the yaml structure that are commented out and discard them and all
            # of their subsequent settings. The top-level key - if commented out -
            # will start with a comment ('#') and immediately be followed by a
            # character. Anything with a space will either have a parent all the
            # way back to the root top-level key, or be an option that needs to be
            # uncommented (like '#     ad: unicodePWd') and dealt with later on in
            # the script. These options (at the point of writing) are only
            # different backends that will be taken care of in a separate function.
            if not last_line_was_commented and line.startswith('# '):
                line = line.replace('#', '')
                commented_file.write(line)
                last_line_was_commented = False
                continue
            elif line.startswith('#'):
                last_line_was_commented = True
                continue
            else:
                last_line_was_commented = False
                commented_file.write(line)


def get_all_ini_settings(filelines):
    """
    Unless ldapcherry is going to maintain a prettily formatted list of all
    of the possible configuration options, or this script can be guaranteed to
    be updated with all possible options, the best way to gather all of them is
    to parse them from the provided sample configuration file.

    While this may seem a little hacky, it is perfectly relevant to a
    configuration file that contains:

        - Commented-out options
        - Commented-out sections
        - Duplicate options in the comments
        - Mutually exclusive options
        - Options that have no periods in their name
        - Options that have one or more periods in their name
        - Options whose default includes "example.com" setups
        - Assumed sane defaults

    This thoroughly prevents any sort of sane parsing without a great deal of
    manipulation. It is easier to hold all available settings in limbo able to
    be tested against than to try to interpret them in a way that could
    potentially be ambiguous in deployment scenarios.

    @list filelines: the lines in the configuration file
    """
    # Create a dict to hold the settings
    all_ini_settings = {}

    #
    # Get all possible settings
    #
    for fileline in filelines:
        # Retrieve and store the section location for reference later
        if fileline.startswith('[') or fileline.startswith('#['):
            section = fileline.replace('[', '').replace(']', '').replace('#', '').strip()
            if section not in all_ini_settings:
                all_ini_settings[section] = {}
            continue
        elif '=' in fileline:
            # Get the option name
            option = fileline.strip().split()[0]
            if option.startswith('#'):
                # This is a commented out option, so we strip the preceeding
                # hash
                option = option[1:]
            setting_index = fileline.index("=")
            # Take a slice of the string right after the index where we find
            # the first equals sign, and then get rid of any leading or
            # trailing whitespace, leaving us with the value of the option.
            setting = fileline[setting_index + 1:].strip()
            # Check if the option already exists in the list of the options
            if not option in all_ini_settings:
                all_ini_settings[section][option] = setting

    return all_ini_settings


def yaml_setup(yaml_filepath, possible_backends, used_backends):
    """
    Handle yaml configuration file initialization if necessary

    @str yaml_filepath: the path to the yaml configuration file
    @list possible_backends: the backends that can be used
    @list used_backends: the backends that are being used
    """
    # Load the yaml
    with open(yaml_filepath, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
            raise SystemExit

    # Since we're naming our environment vars beginning with the name
    # that they belong to (ROLES, ATTRIBUTES) we can simply check to see if
    # the env var we're currently looping over is applicable by just
    # checking to see if the variable starts with the file name that we're
    # currently working on.
    conf_file_name = yaml_filepath.split('/')[-1].split('.')[0]

    # We will, however, make sure to set the defaults for the demo backend.
    config = include_exclude_yaml_backends(config, conf_file_name,
            possible_backends, used_backends)

    # We're not going to read all of the default backends or options since
    # they are largely arbitrary, and realistically should be set up by the
    # admin.
    for env_var in itertools.chain(ldapcherry_default_env_vars, os.environ):
        if env_var.split('__')[0].lower() == conf_file_name:
            config = find_yaml_override(config, env_var)

    # Write the file out
    with open(yaml_filepath, 'w') as configfile:
        yaml.dump(config, configfile, default_flow_style=False)


def ini_setup(all_ini_settings, possible_backends, used_backends):
    """
    Handle ini configuration file initialization if necessary

    @dict all_ini_settings: all of the settings possible in the ini file
    @list possible_backends: the backends that can be used
    @list used_backends: the backends that are being used
    """

    # Set up config parser
    config = configparser.ConfigParser(interpolation=None)
    config.read('/etc/ldapcherry/ldapcherry.ini')

    # Ensure that there are no lingering backend defaults.
    config = include_exclude_ini_backends(config, possible_backends,
            used_backends, all_ini_settings)

    # Set any objects with the ENV VAR value that overrides it.
    # We pass the default env vars first because we definitely want those set,
    # but also allow for the possibility of override later. A for loop's
    # iteration order is controlled by whatever object it's iterating over.
    # Iterating over an ordered collection like a list is guaranteed to iterate
    # over elements in the list's order.
    for env_var in itertools.chain(ldapcherry_default_env_vars, os.environ):
        config = find_ini_override(env_var, config, all_ini_settings)

    # Write the file out
    with open('/etc/ldapcherry/ldapcherry.ini', 'w') as configfile:
        config.write(configfile)

    return possible_backends, used_backends


def conf_setup():
    """
    Set up the ini configuration files if they have not been messed with. This
    is in case the configuration file is being mounted in a docker volume
    which should be considered to be already set up by the admin as opposed
    to a vanilla deploy or another method that does not set the configuration
    file up beforehand.
    """
    #
    # Set up the INI file
    #

    # Read the ini file
    with open('/etc/ldapcherry/ldapcherry.ini', 'r') as file:
        ini_filelines = file.readlines()

    # Make the alternate ini settings available for use.
    all_ini_settings = get_all_ini_settings(ini_filelines)

    # Get the lists of possible and used backends
    possible_backends, used_backends = get_backends(all_ini_settings)

    # We're testing to see if there are any comments in the file since the
    # configuration file as configured by this script has no comments in it.
    if any(fileline.startswith('#') for fileline in ini_filelines):
        ini_setup(all_ini_settings, possible_backends, used_backends)

    #
    # Similarly to the ini file, set up the roles and attributes YAML files.
    # However, here we leave in the extra backends to be taken out later. This
    # is because there are no duplicates, and yaml can parse this just fine,
    # unlike the ini parser which will choke on it if they are all uncommented.
    #

    for yaml_file in ['roles.yml', 'attributes.yml']:
        yaml_filepath = "/etc/ldapcherry/{}".format(yaml_file)
        # Read the YAML file to test for commented-out lines below
        with open(yaml_filepath, 'r') as file:
            yaml_filelines = file.readlines()

        # We're testing to see if there are any comments in the file since the
        # configuration file as configured by this script has no comments in it.
        if any(fileline.startswith('#') for fileline in yaml_filelines):
            # Uncomment all of the yaml setting backends
            all_yaml_settings(yaml_filepath)

            # Configure the yaml conf file given the backends that we're using
            yaml_setup(yaml_filepath, possible_backends, used_backends)



def main():
    conf_setup()
    invocation = ["/usr/local/bin/ldapcherryd", "-c", "/etc/ldapcherry/ldapcherry.ini"]
    try:
        if ast.literal_eval(os.environ['DEBUG']):
            invocation.append("-D")
    except KeyError:
        # The env var `DEBUG` was not specified one way or the other
        pass
    try:
        subprocess.call(invocation)
    except KeyboardInterrupt:
        raise SystemExit

if __name__ == '__main__':
    #
    # Handle ^C without throwing an exception
    #
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit
