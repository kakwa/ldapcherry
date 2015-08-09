Implementing cutom backends
===========================

API
---

The backend modules must respect the following API:

.. autoclass:: ldapcherry.backend.Backend
    :members: __init__, auth, add_user, del_user, set_attrs, add_to_groups, del_from_groups, search, get_user, get_groups
    :undoc-members:
    :show-inheritance:

Configuration
-------------

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

After having set **self.config** to **config** in the constructor, parameters can be recovered
by **self.get_param**:

.. autoclass:: ldapcherry.backend.Backend
    :members: get_param
    :undoc-members:
    :show-inheritance:


Exceptions
----------

The following exception can be used in your module

.. automodule:: ldapcherry.exceptions
    :members: UserDoesntExist, UserAlreadyExists, GroupDoesntExist
    :undoc-members:
    :show-inheritance:

These exceptions permit a nicer error handling and avoid a generic message to be thrown at the user.

Example
-------

Here is the ldap backend module that comes with LdapCherry:

.. literalinclude:: ../ldapcherry/backend/backendDemo.py
    :language: python
