Install
=======

From the sources
----------------

Download the latest release from `GitHub <https://github.com/kakwa/ldapcherry/releases>`_.

.. sourcecode:: bash

    $ tar -xf ldapcherry*.tar.gz
    $ cd ldapcherry*
    $ python setup.py install

From Pypi
---------

.. sourcecode:: bash 

    $ pip install ldapcherry

or

.. sourcecode:: bash

    $ easy_install ldapcherry 

Installed files
---------------

ldapCherry install directories are:

* **/etc/ldapcherry/** (configuration)
* **dist-package** or **site-packages** of your distribution (LdapCherry modules)
* **/usr/share/ldapcherry/** (static content (css, js, images...) and templates)

These directories can be changed by exporting the following variables before launching the install command:

.. sourcecode:: bash

    #optional, default sys.prefix + 'share' (/usr/share/ on most Linux)
    $ export DATAROOTDIR=/usr/local/share/
    #optional, default /etc/
    $ export SYSCONFDIR=/usr/local/etc/ 

