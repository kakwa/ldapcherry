**************
  LdapCherry 
**************

Nice and simple application to manage user and groups in multiple directory services.

----

:Doc: `ldapcherry documentation on ReadTheDoc <http://ldapcherry.readthedocs.org/en/latest/>`_
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
.. raw:: html

    <style>
    #images {
      width: 800px;
      height: 600px;
      overflow: hidden;
      position: relative;
      
      margin: 20px auto;
    }
    #images img {
      width: 800px;
      height: 600px;
      
      position: absolute;
      top: 0;
      left: -400px;
      z-index: 1;
      opacity: 0;
      
      transition: all linear 500ms;
      -o-transition: all linear 500ms;
      -moz-transition: all linear 500ms;
      -webkit-transition: all linear 500ms;
    }
    #images img:target {
      left: 0;
      z-index: 9;
      opacity: 1;
    }
    #images img:first-child {
      left: 0;
      opacity: 1;
    }
    #slider {
      text-align: center;
    }
    #slider a {
      text-decoration: none;
      background: #E3F1FA;
      border: 1px solid #C6E4F2;
      padding: 4px 6px;
      color: #222;
      margin: 20px auto;
    }
    #slider a:hover {
        background: #C6E4F2;
    }
    </style>
    <div id="images">
        <img id="image1" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093051_1438x1064_scrot.png' />
        <img id="image2" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093130_1438x1064_scrot.png' />
        <img id="image3" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093147_1438x1064_scrot.png' />
        <img id="image4" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093152_1438x1064_scrot.png' />
        <img id="image5" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093215_1438x1064_scrot.png' />
        <img id="image6" src='https://raw.githubusercontent.com/kakwa/ldapcherry/master/docs/assets/sc/2015-07-06-093234_1438x1064_scrot.png' />
    </div>
    <div id="slider">
        <a href="#image1">1</a>
        <a href="#image2">2</a>
        <a href="#image3">3</a>
        <a href="#image4">4</a>
        <a href="#image5">5</a>
        <a href="#image6">6</a>
    </div>

`Screenshots <http://ldapcherry.readthedocs.org/en/latest/#image1>`_

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

