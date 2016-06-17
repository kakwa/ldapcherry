Backends
========

Backend id prefix
-----------------

Each parameter of a backend instance must be prefixed by a backend id.
This backend id must be unique.

For example:

.. sourcecode:: ini

    [backends]

    # configuration of the bk1 backend
    bk1.module = 'my.backend.module'
    bk1.display_name = 'My backend module'
    bk1.param = 'value'

.. warning::
    For the rest of the backends documentation, this prefix is inferred.

Common backend parameters
-------------------------

Every backend instance systematicaly has two parameters:

+---------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
|      Parameter      | Section  |            Description             |           Values         |                Comment                     |
+=====================+==========+====================================+==========================+============================================+
| module              | backends | Library path to the module         | Python library path      |                                            |
+---------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| display_name        | backends | Display_name of the backend        | Free text                |                                            |
+---------------------+----------+------------------------------------+--------------------------+--------------------------------------------+

Ldap Backend
------------

Class path
^^^^^^^^^^

The class path for the ldap backend is **ldapcherry.backend.backendLdap**.

Configuration
^^^^^^^^^^^^^

The ldap backend exposes the following parameters:

+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
|      Parameter           | Section  |            Description             |           Values         |                Comment                     |
+==========================+==========+====================================+==========================+============================================+
| uri                      | backends | The ldap uri to access             | ldap uri                 | * use ldap:// for clear/starttls           |
|                          |          |                                    |                          | * use ldaps:// for ssl                     |
|                          |          |                                    |                          | * custom port: ldap://<host>:<port>        |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| ca                       | backends | Path to the CA file                | file path                | optional                                   |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| starttls                 | backends | Use starttls                       | 'on' or 'off'            | optional                                   |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| checkcert                | backends | Check the server certificat        | 'on' or 'off'            | optional                                   |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| binddn                   | backends | The bind dn to use                 | ldap dn                  | This dn must have read/write permissions   |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| password                 | backends | The password of the bind dn        | password                 |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| timeout                  | backends | Ldap connexion timeout             | integer (second)         |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| password                 | backends | The password of the bind dn        | password                 |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| groupdn                  | backends | The ldap dn where groups are       | ldap dn                  |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| userdn                   | backends | The ldap dn where users are        | ldap dn                  |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| user_filter_tmpl         | backends | The search filter template         | ldap search filter       | The user identifier is passed through      |
|                          |          | to recover a given user            | template                 | the **username** variable (*%(username)s*).|
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| group_filter_tmpl        | backends | The search filter template to      | ldap search filter       | The following variables are usable:        |
|                          |          | recover the groups of a given user | template                 | * **username**: the user key attribute     |
|                          |          |                                    |                          | * **userdn**: the user ldap dn             |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| group_attr.<member attr> | backends | Member attribute template value    | template                 | * <member attr> is the member attribute    |
|                          |          |                                    |                          |   in groups dn entries                     |
|                          |          |                                    |                          | * every user attributes are exposed        |
|                          |          |                                    |                          |   in the template                          |
|                          |          |                                    |                          | * multiple attributes can be set           |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| objectclasses            | backends | list of object classes for users   | comma separated list     |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| dn_user_attr             | backends | attribute used in users dn         | dn attribute             |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+


Example
^^^^^^^

.. sourcecode:: ini

    [backends]
    
    # name of the module
    ldap.module = 'ldapcherry.backend.backendLdap'
    # display name of the ldap
    ldap.display_name = 'My Ldap Directory'
    
    # uri of the ldap directory
    ldap.uri = 'ldap://ldap.ldapcherry.org'
    # ca to use for ssl/tls connexion
    #ldap.ca = '/etc/dnscherry/TEST-cacert.pem'
    # use start tls
    #ldap.starttls = 'off'
    # check server certificate (for tls)
    #ldap.checkcert = 'off'
    # bind dn to the ldap
    ldap.binddn = 'cn=dnscherry,dc=example,dc=org'
    # password of the bind dn
    ldap.password = 'password'
    # timeout of ldap connexion (in second)
    ldap.timeout = 1
    
    # groups dn
    ldap.groupdn = 'ou=group,dc=example,dc=org'
    # users dn
    ldap.userdn = 'ou=people,dc=example,dc=org'
    # ldapsearch filter to get a user
    ldap.user_filter_tmpl = '(uid=%(username)s)'
    # ldapsearch filter to get groups of a user
    ldap.group_filter_tmpl = '(member=uid=%(username)s,ou=People,dc=example,dc=org)'
    # filter to search users
    ldap.search_filter_tmpl = '(|(uid=%(searchstring)s*)(sn=%(searchstring)s*))'
    
    # ldap group attributes and how to fill them
    ldap.group_attr.member = "%(dn)s"
    #ldap.group_attr.memberUid = "%(uid)s"
    # object classes of a user entry
    ldap.objectclasses = 'top, person, posixAccount, inetOrgPerson'
    # dn entry attribute for an ldap user
    ldap.dn_user_attr = 'uid'


Active Directory Backend
------------------------

.. warning:: This backend needs the **cn** and **unicodePwd** attributes to be declared in attributes.yml

Class path
^^^^^^^^^^

The class path for the ldap backend is **ldapcherry.backend.backendAD**.

Configuration
^^^^^^^^^^^^^

+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
|      Parameter           | Section  |            Description             |           Values         |                Comment                     |
+==========================+==========+====================================+==========================+============================================+
| uri                      | backends | The ldap uri to access             | ldap uri                 | * use ldap:// for clear/starttls           |
|                          |          |                                    |                          | * use ldaps:// for ssl                     |
|                          |          |                                    |                          | * custom port: ldap://<host>:<port>        |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| ca                       | backends | Path to the CA file                | file path                | optional                                   |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| starttls                 | backends | Use starttls                       | 'on' or 'off'            | optional                                   |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| checkcert                | backends | Check the server certificat        | 'on' or 'off'            | optional                                   |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| domain                   | backends | Name of the domain                 | AD domain                |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| login                    | backends | login used for connecting to AD    | login                    | user used must have sufficient rights      |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+
| password                 | backends | password if binding user           | password                 |                                            |
+--------------------------+----------+------------------------------------+--------------------------+--------------------------------------------+

Example
^^^^^^^

.. sourcecode:: ini


    [backends]

    # Name of the backend
    ad.module = 'ldapcherry.backend.backendAD'
    # display name of the ldap
    ad.display_name = 'My Active Directory'
    # ad domain
    ad.domain = 'dc.ldapcherry.org'
    # ad login
    ad.login  = 'administrator'
    # ad password 
    ad.password = 'qwertyP455'
    # ad uri
    ad.uri = 'ldap://ad.ldapcherry.org'
    
    ## ca to use for ssl/tls connexion
    #ad.ca = '/etc/dnscherry/TEST-cacert.pem'
    ## use start tls
    #ad.starttls = 'off'
    ## check server certificate (for tls)
    #ad.checkcert = 'off'
    
Demo Backend
------------

.. warning:: This backend is only meant for demo.

Class path
^^^^^^^^^^

The class path for the ldap backend is **ldapcherry.backend.backendDemo**.

Configuration
^^^^^^^^^^^^^
+-------------------+----------+----------------------------+----------------------+----------------------------+
|      Parameter    | Section  |            Description     |           Values     |                Comment     |
+===================+==========+============================+======================+============================+
| admin.user        | backends | Login for default admin    | string               | optional, default: 'admin' |
+-------------------+----------+----------------------------+----------------------+----------------------------+
| admin.password    | backends | Password for default admin | string               | optional, default: 'admin' |
+-------------------+----------+----------------------------+----------------------+----------------------------+
| admin.groups      | backends | Groups for default admin   | comma separated list |                            |
+-------------------+----------+----------------------------+----------------------+----------------------------+
| basic.user        | backends | Login for default user     | string               | optional, default: 'user'  |
+-------------------+----------+----------------------------+----------------------+----------------------------+
| basic.password    | backends | Password for default user  | string               | optional, default: 'user'  |
+-------------------+----------+----------------------------+----------------------+----------------------------+
| basic.groups      | backends | Groups for default user    | comma separated list |                            |
+-------------------+----------+----------------------------+----------------------+----------------------------+
| pwd_attr          | backends | Password attribute name    | string               |                            |
+-------------------+----------+----------------------------+----------------------+----------------------------+
| search_attributes | backends | Attributes used for search | comma separated list |                            |
+-------------------+----------+----------------------------+----------------------+----------------------------+

Example
^^^^^^^

.. sourcecode:: ini

    [backends]

    # path to the module
    demo.module = 'ldapcherry.backend.backendDemo'
    # display name of the module
    demo.display_name  = 'Demo Backend'

    ## admin user login (optional, default: 'admin')
    #demo.admin.user = 'admin'
    ## admin user password (optional: default 'admin')
    #demo.admin.password = 'admin'
    # groups for the default admin user (comma separated)
    demo.admin.groups  = 'DnsAdmins'

    ## basic user login (optional, default: 'user')
    #demo.basic.user = 'user'
    ## admin user password (optional: default 'user')
    #demo.basic.password = 'user'
    # groups for the default basic user (comma separated)
    demo.basic.groups  = 'Test 2, Test 1'

    # password attribute used for auth
    demo.pwd_attr = 'userPassword'
    # attributes to search on
    demo.search_attributes = 'cn, sn, givenName, uid'

