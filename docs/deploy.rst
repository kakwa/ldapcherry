Deploy
======

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

General Configuration
---------------------

Logging
~~~~~~~

LdapCherry has two loggers, one for errors and applicative actions (login, del/add, logout...) and one for access logs.

Each logger can be configured to log to syslog, file or be desactivated. 

Syslog parameters:

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

Webserver
~~~~~~~~~

LdapCherry uses the embedded http server of CherryPy, however it has some limitations:

* no listening on port 80/443 (unless run as root, which is strongly discourage)
* no https

The simpler way to properly deploy LdapCherry is to run it listening only on localhost 
with a port above 1024 and put it behind an http server like nginx, apache or lighttpd 
acting as a reverse http(s) proxy.

+---------------------+---------+------------------------------------+--------------------------+----------------------------------------------+
|      Parameter      | Section |            Description             |           Values         |                 Comment                      |
+=====================+=========+====================================+==========================+==============================================+
| server.socket_host  |  global |            Listening IP            |    IP on which to listen |  Use '0.0.0.0' to listen on any interfaces.  |
+---------------------+---------+------------------------------------+--------------------------+----------------------------------------------+
| server.socket_port  |  global |           Listening Port           |            TCP Port      |                                              |
+---------------------+---------+------------------------------------+--------------------------+----------------------------------------------+
| server.thread_pool  |  global |      Number of threads created     |          Number of       |                                              |
|                     |         |       by the CherryPy server       |           threads        |                                              |
+---------------------+---------+------------------------------------+--------------------------+----------------------------------------------+
| tools.staticdir.on  | /static |    Serve static files through      |        True, False       |  These files could be server directly by an  |
|                     |         |            LdapCherry              |                          |     http server for better performance.      |
+---------------------+---------+------------------------------------+--------------------------+----------------------------------------------+
| tools.staticdir.dir | /static |  Directory containing LdapCherry   | Path to static resources |                                              |
|                     |         | static resources (js, css, img...) |                          |                                              |
+---------------------+---------+------------------------------------+--------------------------+----------------------------------------------+

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

Authentication and sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Other LdapCherry parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. sourcecode:: ini

    [global]
    
    # listing interface
    server.socket_host = '127.0.0.1'
    # port
    server.socket_port = 8080
    # number of threads
    server.thread_pool = 8
    #don't show traceback on error
    request.show_tracebacks = False
    
   
    # session configuration
    # activate session
    tools.sessions.on = True
    # session timeout
    tools.sessions.timeout = 10
    # file session storage(to use if multiple processes, 
    # default is in RAM and per process)
    #tools.sessions.storage_type = "file"
    # session 
    #tools.sessions.storage_path = "/var/lib/ldapcherry/sessions"
    
    # resources parameters
    [resources]
    # templates directory
    template_dir = '/usr/share/ldapcherry/templates/'
    
    # enable cherrypy static handling
    # to comment if static content are handled otherwise
    [/static]
    tools.staticdir.on = True
    tools.staticdir.dir = '/usr/share/ldapcherry/static/'

LdapCherry full configuration file
----------------------------------

.. literalinclude:: ../conf/ldapcherry.ini
   :language: ini


Init Script
-----------

Sample init script for Debian:

.. literalinclude:: ../goodies/init-debian
   :language: bash

This init script is available in **goodies/init-debian**.


