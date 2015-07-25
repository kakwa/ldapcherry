Implementing password policy modules
====================================

API
---

The password policy modules must respect following API:

.. autoclass:: ldapcherry.ppolicy.PPolicy
    :members: check, info, __init__
    :undoc-members:
    :show-inheritance:

Configuration
-------------

Parameters are declared in the main configuration file, inside the **ppolicy** section.

After having set **self.config** to **config** in the constructor, parameters can be recovered
by **self.get_param**:

.. autoclass:: ldapcherry.ppolicy.PPolicy
    :members: get_param
    :undoc-members: check
    :show-inheritance:

Example
-------

Here is the simple default ppolicy module that comes with LdapCherry:

.. literalinclude:: ../ldapcherry/ppolicy/simple.py
    :language: python

