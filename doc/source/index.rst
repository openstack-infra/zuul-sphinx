.. include:: ../../README.rst

Overview
--------

This documentation has full examples of how to use the zuul-sphinx
features.

Config options
--------------

The following options can be set

.. attr:: zuul_role_paths
   :type: str list

   List of extra paths to examine for role documentation (other than
   ``roles/``)

.. attr:: zuul_roles_warn_missing
   :type: bool
   :default: True

    Warn when a role found with ``autoroles`` does not have a
    ``README.rst`` file.


Examples
--------

.. note::

   To see the commands that produces the rendered output for this page
   or any of the examples below, use the ``Show Source`` link at the
   bottom of the page.

.. toctree::
   :maxdepth: 2

   example-variables
   example-attributes
   example-jobs
   example-templates
   example-roles
   example-autodoc
   example-statistics

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
