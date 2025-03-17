**************
  LdapCherry 
**************

.. image:: https://raw.githubusercontent.com/kakwa/ldapcherry/master/resources/static/img/apple-touch-icon-72-precomposed.png

Nice and simple application to manage users and groups in multiple directory services.

.. image:: https://github.com/kakwa/ldapcherry/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/kakwa/ldapcherry/actions/workflows/tests.yml
    :alt: CI
    
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


Debian and RPM packages are also available here: `https://github.com/kakwa/kakwalab-pkg` (package name ``ldapcherry``).

***********
  License
***********

LdapCherry is published under the MIT Public License.

*******************************
  Discussion / Help / Updates
*******************************

* IRC: `Libera <https://libera.chat/>`_ ``#ldapcherry`` channel
* Bugtracker: `Github <https://github.com/kakwa/ldapcherry/issues>`_

----

.. image:: https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/python-powered.png
.. image:: https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/cherrypy.png
