Zuul Sphinx
===========

A Sphinx extension for documenting Zuul jobs.

Config options
--------------

``zuul_role_paths``
  (str list)
  List of extra paths to examine for role documentation (other than
  ``roles/``)

``zuul_autoroles_warn_missing``
  (boolean)
  Default: True
  Warn when a role found with ``autoroles`` does not have a
  ``README.rst`` file.
