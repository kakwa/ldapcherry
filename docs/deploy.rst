Deploy
======

LdapCherry aims to be as simple as possible to deploy.
The Application is constituted of:

* ldapcherryd: the daemon to lauch LdapCherry.
* one ini file (ldapcherry.ini by default): the entry point for the configuration, containing all the "technical" attributes.
* two yaml files (roles.yml and attributes by default): the files containing the roles and attributes definition.

The default configuration directory is **/etc/ldapcherry/**.

Launch
------

LdapCherry is launched using the internal cherrypy server:


.. sourcecode:: bash

    # ldapcherryd help
    $ ldapcherryd -h

    # launching ldapcherryd in the forground
    $ ldapcherryd -c /etc/ldapcherry/ldapcherry.ini

    # launching ldapcherryd as a daemon
    $ ldapcherryd -c /etc/ldapcherry/ldapcherry.ini -p /var/run/ldapcherry/ldapcherry.pid -d

Roles and Attributes Configuration
----------------------------------

Entry point in main configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main configuration file (**ldapcherry.ini** by default) contains two parameters locating the roles and attributes configuration files:

+-----------------+------------+-------------------------------+-------------------+
|   Parameter     |  Section   |            Description        |       Values      |
+=================+============+===============================+===================+
| attributes.file | attributes | Attributes configuration file | Path to conf file |
+-----------------+------------+-------------------------------+-------------------+
| roles.file      | roles      | Roles configuration file      | Path to conf file |
+-----------------+------------+-------------------------------+-------------------+

Attributes Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

The attributes configuration is done in a yaml file (**attributes.yml** by default).

Mandatory parameters
^^^^^^^^^^^^^^^^^^^^

The mandatory parameters for an attribute, and their format are the following:

.. sourcecode:: yaml

    <attr id>:
        description: <Human readable description of the attribute>                       # (free text)
        display_name: <Display name in LdapCherry forms>                                 # (free text)
        weight: <weight controlling the display order of the attributes, lower is first> # (integer)
        type: <type of the attributes>                                                   # (in ['int', 'string', 'email', 'stringlist', 'fix'])
        backends:                                                                        # (list of backend attributes name)
            - <backend id 1>: <backend 1 attribute name>
            - <backend id 2>: <backend 2 attribute name>

.. warning::

    <attr id> (the attribute id) must be unique, LdapCherry won't start if it's not.

.. warning::

    <backend id> (the backend id) must be defined in main ini configuration file.
    LdapCherry won't start if it's not.

Type stringlist values
^^^^^^^^^^^^^^^^^^^^^^

If **type** is set to **stringlist** the parameter **values** must be filled with the list of possible values:

.. sourcecode:: yaml

    <attr id>:
        description: <Human readable description of the attribute>
        display_name: <Display name in LdapCherry forms>
        weight: <weight controlling the display order of the attributes)

        type: stringlist
        values:
            - value1
            - value2
            - value3

        backends:
            - <backend id>: <backend attribute name>

Key attribute:
^^^^^^^^^^^^^^

One attribute must be used as a unique key across all backends:

To set the key attribute, you must set **key** to **True** on this attribute.

Example:

.. sourcecode:: yaml

    uid:
        description: "UID of the user"
        display_name: "UID"
        search_displayed: True
        key: True                       # defining the attribute as "key"
        type: string
        weight: 50
        backends:
            ldap: uid
            ad: sAMAccountName

Authorize self modification
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A user can modify some of his attributes (self modification). 
In such case, the parameter **self** must set to **True**:

.. sourcecode:: yaml

    <attr id>:
        description: <Human readable description of the attribute>
        display_name: <Display name in LdapCherry forms>
        weight: <weight controlling the display order of the attributes)
        type: <type of the attributes>

        self: True

        backends:
            - <backend id 1>: <backend 1 attribute name>
            - <backend id 2>: <backend 2 attribute name>

Autofill
^^^^^^^^

LdapCherry has the possibility to auto-fill fields from other fields, 
to use this functionnality **autofill** must be set.

Example:

.. sourcecode:: yaml

    gidNumber:
        description: "Group ID Number of the user"
        display_name: "GID Number"
        weight: 70
        type: int
    
        autofill:
            function: lcUidNumber # name of the function to call
            args:                 # list of arguments
                - $first-name     # 
                - $name
                - '10000'
                - '40000'
    
        backends:
            ldap: gidNumber

Arguments of the **autofill** function work as follow:

* if argument starts with **$**, for example **$my_field**, the value of form input **my_field** will be passed to the function.
* otherwise, it will be treated as a fixed argument.

Available **autofill** functions:

* lcUid: generate 8 characters ascii uid from 2 other fields (first letter of the first field, 7 first letters of the second):

.. sourcecode:: yaml

    autofill: 
        function: lcUid
        args:
            - $first-name
            - $name


* lcDisplayName: concatenate two fields (with a space as separator):

.. sourcecode:: yaml

    autofill: 
        function: lcDisplayName
        args:
            - $first-name
            - $name

* lcMail: generate an email address from 2 other fields and a domain (<uid>+domain):

.. sourcecode:: yaml

    autofill: 
        function: lcMail
        args:
            - $first-name
            - $name
            - '@example.com'


* lcUidNumber: generate an uid number from 2 other fields and between a minimum and maximum value:

.. sourcecode:: yaml

    autofill: 
        function: lcUidNumber
        args:
            - $first-name
            - $name
            - '10000'
            - '40000'

* lcHomeDir: generate an home directory from 2 other fields and a root (<root>+<uid>):

.. sourcecode:: yaml

    autofill: 
        function: lcHomeDir
        args:
            - $first-name
            - $name
            - /home/

Roles Configuration
~~~~~~~~~~~~~~~~~~~

The roles configuration is done in a yaml file (**roles.yml** by default).

Mandatory parameters
^^^^^^^^^^^^^^^^^^^^

Roles are seen as an aggregate of groups:

.. sourcecode:: yaml

    <role id>:
        display_name: <role display name in LdapCherry>
        description: <human readable role description>  
        backends_groups:                                # list of backends
            <backend id 1>:                             # list of groups in backend
                - <b1 group 1>
                - <b1 group 2>
            <backend id 2>:
                - <b2 group 1>
                - <b2 group 2>

.. warning:: <role id> must be unique, LdapCherry won't start if it's not

Defining LdapCherry Administrator role
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At least one of the declared roles must be tagged to be LdapCherry administrators.

Doing so is done by setting **LC_admins** to **True** for the selected role:

.. sourcecode:: yaml

    <role id>:
        display_name: <Role display name in LdapCherry>
        description: <human readable role description>  

        LC_admins: True

        backends_groups:                                # list of backends
            <backend id 1>:                             # list of groups in backend
                - <b1 group 1>
                - <b1 group 2>
            <backend id 2>:
                - <b2 group 1>
                - <b2 group 2>

Nesting roles
^^^^^^^^^^^^^

LdapCherry handles roles nesting:

.. sourcecode:: yaml

    parent_role:
        display_name: Role parent
        description: The parent role
        backends_groups:
            backend_id_1:
                - b1_group_1
                - b1_group_2
            backend_id_2:
                - b2_group_1
                - b2_group_2
        subroles:
            child_role_1:
                display_name: Child role 1
                description: The first Child Role
                backends_groups:
                    backend_id_1:
                        - b1_group_3
            child_role_2:
                display_name: Child role 2
                description: The second Child Role
                backends_groups:
                    backend_id_1:
                        - b1_group_4

In that case, child_role_1 and child_role_2 will contain all groups of parent_role plus their own specific groups.

Main Configuration
------------------

Webserver
~~~~~~~~~

LdapCherry uses the embedded http server of CherryPy, however it has some limitations:

* no listening on port 80/443 (unless run as root, which is strongly discourage)
* no https

The simpler way to properly deploy LdapCherry is to run it listening only on localhost 
with a port above 1024 and put it behind an http server like nginx, apache or lighttpd 
acting as a reverse http(s) proxy.

+---------------------+---------+------------------------------------+--------------------------+--------------------------------------------+
|      Parameter      | Section |            Description             |           Values         |                Comment                     |
+=====================+=========+====================================+==========================+============================================+
| server.socket_host  |  global | Listening IP                       | IP on which to listen    | Use '0.0.0.0' to listen on any interfaces. |
+---------------------+---------+------------------------------------+--------------------------+--------------------------------------------+
| server.socket_port  |  global | Listening Port                     | TCP Port                 |                                            |
+---------------------+---------+------------------------------------+--------------------------+--------------------------------------------+
| server.thread_pool  |  global | Number of threads created          | Number of threads        |                                            |
|                     |         | by the CherryPy server             | threads                  |                                            |
+---------------------+---------+------------------------------------+--------------------------+--------------------------------------------+
| tools.staticdir.on  | /static | Serve static files through         | True, False              | These files could be server directly by an |
|                     |         | LdapCherry                         |                          | HTTP server for better performance.        |
+---------------------+---------+------------------------------------+--------------------------+--------------------------------------------+
| tools.staticdir.dir | /static | Directory containing LdapCherry    | Path to static resources |                                            |
|                     |         | static resources (js, css, img...) |                          |                                            |
+---------------------+---------+------------------------------------+--------------------------+--------------------------------------------+

example:

.. sourcecode:: ini

    [global]
    
    # listing interface
    server.socket_host = '127.0.0.1'
    # port
    server.socket_port = 8080
    # number of threads
    server.thread_pool = 8
   
    # enable cherrypy static handling
    # to comment if static content are handled otherwise
    [/static]
    tools.staticdir.on = True
    tools.staticdir.dir = '/usr/share/ldapcherry/static/'

Backends
~~~~~~~~

Backends are configure in the **backends** section, the format is the following:


.. sourcecode:: ini

    [backends]

    # backend python module path
    <backend id>.module = <python.module.path>

    # display name of the backend in forms
    <backend id>.display_name = <display name of the backend> 

    # parameters of the module instance for backend <backend id>.
    <backend id>.<param> = <value>

It's possible to instanciate the same module several times.

Authentication and sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

LdapCherry supports several authentication modes:

+------------------------+---------+---------------------+------------------------------------------------+---------------------------------+
|        Parameter       | Section |     Description     |                  Values                        |             Comment             |
+========================+=========+=====================+================================================+=================================+
| auth.mode              | auth    | Authentication mode | * 'and' (user must auth on all backends)       |                                 |
|                        |         |                     | * 'or' (user must auth on one of the backends) |                                 |
|                        |         |                     | * 'none' (disable auth)                        |                                 |
|                        |         |                     | * 'custom' (use custom auth module)            |                                 |
+------------------------+---------+---------------------+------------------------------------------------+---------------------------------+
| auth.module            | auth    | Custom auth module  | python class path to module                    | only used if auth.mode='custom' |
+------------------------+---------+---------------------+------------------------------------------------+---------------------------------+
| tools.sessions.timeout | global  | Session timeout in  | Number of minutes                              |                                 |
|                        |         | minutes             |                                                |                                 |
+------------------------+---------+---------------------+------------------------------------------------+---------------------------------+

Different session backends can also be configured (see CherryPy documentation for details)

.. sourcecode:: ini

    [global]
    # session configuration
    # activate session
    tools.sessions.on = True
    # session timeout in minutes
    tools.sessions.timeout = 10
    # file session storage(to use if multiple processes, 
    # default is in RAM and per process)
    #tools.sessions.storage_type = "file"
    # session 
    #tools.sessions.storage_path = "/var/lib/ldapcherry/sessions"

    [auth]
    # Auth mode
    # * and: user must authenticate on all backends
    # * or:  user must authenticate on one of the backend
    # * none: disable authentification
    # * custom: custom authentification module (need auth.module param)
    auth.mode = 'or'

    # custom auth module to load
    #auth.module = 'ldapcherry.auth.modNone'

Logging
~~~~~~~

LdapCherry has two loggers, one for errors and applicative actions (login, del/add, logout...) and one for access logs.

Each logger can be configured to log to syslog, file or be disabled. 

Logging parameters:

+--------------------+---------+---------------------------------+-------------------------------------------------+----------------------------------------+
|      Parameter     | Section |           Description           |                      Values                     |                 Comment                |
+====================+=========+=================================+=================================================+========================================+
| log.access_handler |  global |    Logger type for access log   |            'syslog', 'file', 'none'             |                                        |
+--------------------+---------+---------------------------------+-------------------------------------------------+----------------------------------------+
|  log.error_handler |  global | Logger type for applicative log |             'syslog', 'file', 'none'            |                                        |
+--------------------+---------+---------------------------------+-------------------------------------------------+----------------------------------------+
|   log.access_file  |  global |     log file for access log     |                 path to log file                | only used if log.access_handler='file' |
+--------------------+---------+---------------------------------+-------------------------------------------------+----------------------------------------+
|   log.error_file   |  global |   log file for applicative log  |                 path to log file                |  only used if log.error_handler='file' |
+--------------------+---------+---------------------------------+-------------------------------------------------+----------------------------------------+
|      log.level     |  global |     log level of LdapCherry     | 'debug', 'info', 'warning', 'error', 'critical' |                                        |
+--------------------+---------+---------------------------------+-------------------------------------------------+----------------------------------------+

Example:

.. sourcecode:: ini

    [global]

    # logger syslog for access log 
    log.access_handler = 'syslog'
    # logger syslog for error and ldapcherry log 
    log.error_handler = 'syslog'
    # log level
    log.level = 'info'


Custom javascript
~~~~~~~~~~~~~~~~~

It's possible to add custom javascript to LdapCherry, mainly to add custom autofill functions.

Configuration:

+---------------------+---------+--------------------------------+--------------------------+------------------------------------------------------------+
|      Parameter      | Section |            Description         |           Values         |                Comment                                     |
+=====================+=========+================================+==========================+============================================================+
| tools.staticdir.on  | /custom | Serve custom js files through  | True, False              | These files could be server directly by an                 |
|                     |         | LdapCherry                     |                          | HTTP server for better performance.                        |
+---------------------+---------+--------------------------------+--------------------------+------------------------------------------------------------+
| tools.staticdir.dir | /custom | Directory containing custom js | Path to static resources | * custom js files must be put at the root if the directory |
|                     |         | files                          |                          | * only files ending with ".js" are taken into account      |
+---------------------+---------+--------------------------------+--------------------------+------------------------------------------------------------+


Other LdapCherry parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

+---------------+-----------+--------------------------------+------------------------+
|   Parameter   |  Section  |           Description          |      Values            |
+===============+===========+================================+========================+
| template_dir  | resources | LdapCherry template directory  |  path to template dir  |
+---------------+-----------+--------------------------------+------------------------+

.. sourcecode:: ini

    # resources parameters
    [resources]
    # templates directory
    template_dir = '/usr/share/ldapcherry/templates/'
    
