**************
  LdapCherry 
**************

.. image:: https://raw.githubusercontent.com/kakwa/ldapcherry/master/resources/static/img/apple-touch-icon-72-precomposed.png

Nice and simple application to manage users and groups in multiple directory services.

.. image:: https://travis-ci.org/kakwa/ldapcherry.svg?branch=master
    :target: https://travis-ci.org/kakwa/ldapcherry
    
.. image:: https://coveralls.io/repos/kakwa/ldapcherry/badge.svg 
    :target: https://coveralls.io/r/kakwa/ldapcherry

.. image:: https://img.shields.io/pypi/dm/ldapcherry.svg
    :target: https://pypi.python.org/pypi/ldapcherry
    :alt: Number of PyPI downloads
    
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

It's main features are:

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

    # change the directory where to put the configuration (default: /etc)
    $ export SYSCONFDIR=<sys conf dir>
    
    # install ldapcherry
    $ pip install ldapcherry

    # edit configuration files
    $ vi /etc/ldapcherry/ldapcherry.ini
    $ vi /etc/ldapcherry/roles.yml
    $ vi /etc/ldapcherry/attributes.yml

    # launch ldapcherry
    $ ldapcherryd -c /etc/ldapcherry/ldapcherry.ini


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
