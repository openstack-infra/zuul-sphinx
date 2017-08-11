Example Roles
=============

Roles
-----

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

This is an (Ansible) role (Sphinx) role: :role:`example`

This is an (Ansible) role variable (Sphinx) role: :rolevar:`example.items.baz`
