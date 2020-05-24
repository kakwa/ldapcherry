**************
  LdapCherry
**************

.. image:: https://raw.githubusercontent.com/kakwa/ldapcherry/master/resources/static/img/apple-touch-icon-72-precomposed.png

Nice and simple application to manage users and groups in multiple directory services.

.. image:: https://travis-ci.org/kakwa/ldapcherry.svg?branch=master
    :target: https://travis-ci.org/kakwa/ldapcherry

.. image:: https://coveralls.io/repos/kakwa/ldapcherry/badge.svg 
    :target: https://coveralls.io/r/kakwa/ldapcherry

.. image:: https://img.shields.io/pypi/v/ldapcherry.svg
    :target: https://pypi.python.org/pypi/ldapcherry
    :alt: PyPI version

.. image:: https://readthedocs.org/projects/ldapcherry/badge/?version=latest
    :target: http://ldapcherry.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

----

:Doc:    `LdapCherry documentation on ReadTheDoc <http://ldapcherry.readthedocs.org/en/latest/>`_
:Dev:    `LdapCherry source code on GitHub <https://github.com/kakwa/ldapcherry>`_
:PyPI:   `LdapCherry package on Pypi <http://pypi.python.org/pypi/ldapcherry>`_
:License: MIT
:Author:  Pierre-Francois Carpentier - copyright © 2016

----

********
  Demo
********

A demo is accessible here: https://ldapcherry.kakwalab.ovh

The credentials are:

* as administrator: admin/admin
* as user: user/user

Please take note that it's not possible to modify/delete the 'admin' and 'user' users.

Also take note that the service will be reseted once per day.

****************
  Presentation
****************

LdapCherry is a CherryPY application to manage users and groups in multiple directory services.

Its main features are:

* manage multiple directories/databases backends in an unified way
* roles management (as in "groups of groups")
* autofill forms
* password policy
* self modification of some selected fields by normal (non administrator) users
* nice bootstrap interface
* modular through pluggable authentication, password policy and backend modules

LdapCherry is not limited to ldap, it can handle virtually any user backend (ex: SQL database, htpasswd file, etc)
through the proper plugin (provided that it is implemented ^^).

LdapCherry also aims to be as simple as possible to deploy: no crazy dependencies, 
few configuration files, extensive debug logs and full documentation.

The default backend plugins permit to manage Ldap and Active Directory.

***************
  Screenshots
***************

`Screenshots <http://ldapcherry.readthedocs.org/en/latest/screenshots.html#image1>`_.

***********
  Try out
***********

.. sourcecode:: bash

    # clone the repository
    $ git clone https://github.com/kakwa/ldapcherry && cd ldapcherry

    # change the directory where to put the configuration (default: /etc)
    $ export SYSCONFDIR=/etc
    # change the directory where to put the resource (default: /usr/share)
    $ export DATAROOTDIR=/usr/share/

    # install ldapcherry
    $ python setup.py install

    # edit configuration files
    $ vi /etc/ldapcherry/ldapcherry.ini
    $ vi /etc/ldapcherry/roles.yml
    $ vi /etc/ldapcherry/attributes.yml

    # launch ldapcherry
    $ ldapcherryd -c /etc/ldapcherry/ldapcherry.ini -D

**********
  Docker
**********

Building and running
^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: bash

    # Build the docker container with the tag ldapcherry
    $ docker build -t ldapcherry .

    # Run the docker container tagged as ldapcherry with the demo backend
    # and allow incoming requests on port 8080 on the localhost
    $ docker run -p 8080:8080 ldapcherry

Default environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+-----------------------------+-------------------------------------+-----------------------+-------------------------+
|  Environment Variable Name  |  Description                        |  Default              |  Values                 |
+=============================+=====================================+=======================+=========================+
| ``DEBUG``                   | Run the container in debug mode     | ``False``             | * ``True``              |
|                             |                                     |                       | * ``False``             |
+-----------------------------+-------------------------------------+-----------------------+-------------------------+
| ``SUFFIX``                  | Set the suffix for the domain       | ``dc=example,dc=org`` | * ``example.org``       |
|                             |                                     |                       | * ``dc=example,dc=org`` |
+-----------------------------+-------------------------------------+-----------------------+-------------------------+
| ``SERVER_SOCKET_HOST``      | IP address for the daemon to run on | ``0.0.0.0``           | IP Address              |
+-----------------------------+-------------------------------------+-----------------------+-------------------------+
| ``SERVER_SOCKET_PORT``      | Port for the daemon to run on       | ``8080``              | Unprivileged Port       |
+-----------------------------+-------------------------------------+-----------------------+-------------------------+
| ``LOG_ACCESS_HANDLER``      | The target for the access logs      | ``stdout``            | * ``stdout``            |
|                             |                                     |                       | * ``file``              |
|                             |                                     |                       | * ``syslog``            |
|                             |                                     |                       | * ``none``              |
+-----------------------------+-------------------------------------+-----------------------+-------------------------+
| ``LOG_ERROR_HANDLER``       | The target for the error logs       | ``stdout``            | * ``stdout``            |
|                             |                                     |                       | * ``file``              |
|                             |                                     |                       | * ``syslog``            |
|                             |                                     |                       | * ``none``              |
+-----------------------------+-------------------------------------+-----------------------+-------------------------+

.. warning::

    Setting either of the ``LOG_<TYPE>_HANDLER`` variables to ``file`` requires the appropriate ``LOG_<TYPE>_FILE`` to be set

Other environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^

All other confguration options are parsed programatically from environment variables that are formatted differently for the two file types -- one way for the ``ini`` file and another for the ``.yml`` file.

INI configuration file
^^^^^^^^^^^^^^^^^^^^^^

The environment variables that should be passed to the ``ldapcherry.ini`` configuration file are only to be made into upper-case underscore-separated versions of the options inside of each section of the ldapcherry.ini file. For instance:

::

  server.socket_host -> SERVER_SOCKET_HOST
  request.show_tracebacks -> REQUEST_SHOW_TRACEBACKS
  tools.sessions.timeout -> TOOLS_SESSIONS_TIMEOUT
  min_length -> MIN_LENGTH

They will be put into their respective sections in the ldapcherry.ini file.

YAML configuration files
^^^^^^^^^^^^^^^^^^^^^^^^

For the yaml configuration files (``attributes.yml`` and ``roles.yml``), the environment variable name is programatically parsed based on the following template:

::

  <FILENAME (without the .yml extension)>__<ATTRIBUTE ID>__<PARAMETER>

The following example demonstrates how to customize the ``shell`` attribute ID in the ``attributes.yml`` file:

::

  shell:
      description: "Shell of the user"
      display_name: "Shell"
      weight: 80
      values:
          - /bin/bash
          - /bin/zsh
          - /bin/sh

::

  ATTRIBUTES__SHELL__DESCRIPTION="Shell of the user"
  ATTRIBUTES__SHELL__DISPLAY_NAME="Shell"
  ATTRIBUTES__SHELL__WEIGHT="80"
  ATTRIBUTES__SHELL__VALUES="['/bin/bash', '/bin/zsh', '/bin/sh']"

***********
  License
***********

LdapCherry is published under the MIT Public License.

*******************************
  Discussion / Help / Updates
*******************************

* IRC: `Freenode <http://freenode.net/>`_ ``#ldapcherry`` channel
* Bugtracker: `Github <https://github.com/kakwa/ldapcherry/issues>`_

----

.. image:: https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/python-powered.png
.. image:: https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/cherrypy.png
