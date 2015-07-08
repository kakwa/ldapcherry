==============
  LdapCherry 
==============

Nice and simple application to manage user and groups in multiple directory services.

----

:Dev: `ldapcherry code on GitHub <https://github.com/kakwa/ldapcherry>`_
:PyPI: `ldapcherry package on Pypi <http://pypi.python.org/pypi/ldapcherry>`_
:License: MIT
:Author: Pierre-Francois Carpentier - copyright © 2015

----

.. image:: https://travis-ci.org/kakwa/ldapcherry.svg?branch=master
    :target: https://travis-ci.org/kakwa/ldapcherry
    
.. image:: https://coveralls.io/repos/kakwa/ldapcherry/badge.svg 
    :target: https://coveralls.io/r/kakwa/ldapcherry

****************
  Presentation
****************

LdapCherry is CherryPY application to manage users and groups in directory services.

Applications like phpLDAPadmin tend to have some serious limitations. They are great at
managing individual attributes in an ldap directory, but exposing those raw attributes
is a bit rough, and cannot be put in everybody's hands. Further more, managing groups
can be a chore. Finally, managing multiple directories (or other any form of user databases)
is impossible (It's common to have an Active Directory and an OpenLdap directory 
on most infrastructures, managing them in a unified way could be nice). Not to mention that 
most of these application are quite old (and ugly).

LdapCherry aims to fix that, it provides simple and nice add/modified form, roles handling
(roles are groups aggregate in LdapCherry), user self modification and search.
It can handle multiple user back-ends in a unified way, check password policy.

LdapCherry is also highly modular, with the possibility to implement your own plugins for
the user back-ends, the authentication and the password policy.

LdapCherry also aims to be as simple as possible to deploy: no crazy dependencies, few configuration files and extensive debug logs.

**************
  Screenshot
**************

`Screenshots directory <https://github.com/kakwa/ldapcherry/tree/master/docs/assets/sc>`_

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

.. image:: docs/assets/python-powered.png
.. image:: docs/assets/cherrypy.png

