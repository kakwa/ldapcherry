Some Goodies
============

Here are some goodies that might help deploying LdapCherry

They are located in the **goodies/** directory.

Init Script
-----------

Sample init script for Debian:

.. literalinclude:: ../goodies/init-debian
    :language: bash

This init script is available in **goodies/init-debian**.

Apache Vhost
------------

Basic Apache Vhost:

.. literalinclude:: ../goodies/apache.conf
    :language: xml

Nginx Vhost
-----------

Basic Nginx Vhost:

.. literalinclude:: ../goodies/nginx.conf
    :language: yaml

Nginx Vhost (FastCGI)
---------------------

Nginx Vhost in FastCGI mode:

.. literalinclude:: ../goodies/nginx-fastcgi.conf
    :language: yaml

.. warning::

    LdapCherry requires the python flup module to run in FastCGI

Lighttpd Vhost
--------------

Basic Lighttpd Vhost

.. literalinclude:: ../goodies/lighttpd.conf
    :language: yaml

Demo Backend Configuration Files
--------------------------------

The files here are the ones that are used at the demo site at `ldapcherry.kakwalab.ovh <https://ldapcherry.kakwalab.ovh/>`_ and can be used for a self-hosted demo backend:

.. literalinclude:: ../goodies/demo_backend_configs/attributes.yml
    :language: yaml

.. literalinclude:: ../goodies/demo_backend_configs/roles.yml
    :language: yaml

.. literalinclude:: ../goodies/demo_backend_configs/ldapcherry.ini
    :language: ini
