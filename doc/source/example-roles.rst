Roles
=====

.. role:: example

   This is an example role.

   **Role Variables**

   .. rolevar:: foo

      This is a variable used by this role.

      .. rolevar:: bar
         :default: zero

         This is a sub key.

   .. rolevar:: items
      :type: list

      This variable is a list.

      .. rolevar:: baz

         This is an item in a list.

   .. rolevar:: dict
      :type: dict

      This variable is a dict.

      .. rolevar:: key

         This is a key which should be assigned a value.

   .. rolevar:: flag-value
      :type: bool
      :default: False

      A variable which should be assigned a True/False value.

This is an (Ansible) role (Sphinx) role: :role:`example`

This is an (Ansible) role variable (Sphinx) role: :rolevar:`example.items.baz`
