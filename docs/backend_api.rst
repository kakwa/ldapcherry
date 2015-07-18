Implementing your own backend
=============================

API
~~~

To create your own backend, you must implement the following API:

.. automodule:: ldapcherry.backend
    :members:
    :undoc-members:
    :show-inheritance:

Configuration
~~~~~~~~~~~~~

Configuration for your backend is declared in the main ini file, inside [backends] section:

For example with the configuration:

.. sourcecode:: ini

    [backends]

    # class path to module
    b_id.module = "my.backend.module"

    b_id.param1 = "my value 1"
    b_id.param2 = "my value 2"

.. note::

    One module can be instanciated several times, the prefix b_id permits
    to differenciate instances and their specific configuration.

The following hash will be passed as configuration to the module constructor as parameter config:

.. sourcecode:: python

    {
        'param1': "my value 1",
        'param2': "my value 2",
    }

Exceptions
~~~~~~~~~~
The following exception can be used in your module

*
*
*
*

These exceptions permit a nicer error handling and avoid a generic message to be thrown at the user.
