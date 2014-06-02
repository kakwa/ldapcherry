Deploy
======

Launching LdapCherry
-------------------

ldapCherry can be launch using cherrypy internal webserver:


.. sourcecode:: bash

    # ldapcherryd help
    $ ldapcherryd -h
    Usage: ldapcherryd [options]
    
    Options:
      -h, --help            show this help message and exit
      -c CONFIG, --config=CONFIG
                            specify config file
      -d                    run the server as a daemon
      -e ENVIRONMENT, --environment=ENVIRONMENT
                            apply the given config environment
      -f                    start a fastcgi server instead of the default HTTP
                            server
      -s                    start a scgi server instead of the default HTTP server
      -x                    start a cgi server instead of the default HTTP server
      -p PIDFILE, --pidfile=PIDFILE
                            store the process id in the given file
      -P PATH, --Path=PATH  add the given paths to sys.path

    # launching ldapcherryd
    $ ldapcherryd -c /etc/ldapcherry/ldapcherry.ini

ldap Configuration
-----------------


Logs
----

ldapCherry has two loggers, one for errors and actions (login, del/add, logout...) and one for access logs.
Each logger can be configured to log to syslog, file or be unactivated. 

.. warning::

    you can't set a logger to log both in file and syslog

Syslog configuration:

.. sourcecode:: ini

    [global]

    # logger syslog for access log 
    log.access_handler = 'syslog'
    # logger syslog for error and ldapcherry log 
    log.error_handler = 'syslog'

File configuration:

.. sourcecode:: ini

    [global]

    # logger syslog for access log 
    log.access_handler = 'file'
    # logger syslog for error and ldapcherry log 
    log.error_handler = 'file'
    # access log file
    log.access_file = '/tmp/ldapcherry_access.log'
    # error and ldapcherry log file
    log.error_file = '/tmp/ldapcherry_error.log'

Disable logs:

.. sourcecode:: ini

    [global]

    # logger syslog for access log 
    log.access_handler = 'none'
    # logger syslog for error and ldapcherry log 
    log.error_handler = 'none'

Set log level:

.. sourcecode:: ini

    [global]

    # log level
    log.level = 'info'

Other ldapCherry parameters
--------------------------

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

WebServer
---------

Idealy, LdapCherry must be deployed behind a proper http server like nginx or apache.

The webserver must be configured to act as a reverse (ssl) proxy to a ldapCherry instance listening on localhost (127.0.0.1).

Cherrypy
~~~~~~~~

Cherrypy has an embeded web sever which can be used for testing.

It has some severe limitations:

* no SSL/TLS (which is recommanded)
* no listening on the standard http port 80

To make ldapCherry listens on every IP:

.. sourcecode:: ini

    [global]
    
    # listing interface
    server.socket_host = '0.0.0.0'
    # port
    server.socket_port = 8080
 
Nginx
~~~~~

.. literalinclude:: ../goodies/nginx.conf
   :language: none


Apache
~~~~~~

.. literalinclude:: ../goodies/apache.conf
   :language: none

Lighttpd
~~~~~~~~

.. literalinclude:: ../goodies/lighttpd.conf
   :language: none

Init Script
-----------

Sample init script for Debian:

.. literalinclude:: ../goodies/init-debian
   :language: bash

This init script is available in **goodies/init-debian**.

ldapCherry configuration file
----------------------------

.. literalinclude:: ../conf/ldapcherry.ini
   :language: ini

