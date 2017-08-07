Examples
========

Jobs
----

.. job:: example-job

   This is an example job.

   .. var:: foo

      This is a variable used by this job.

      .. var:: bar

         This is a sub key.

   .. var:: items
      :type: list

      This variable is a list.

      .. var:: baz

         This is an item in a list.

.. job:: example-job
   :variant: stable

   This is a variant of :job:`example-job` which runs on stable branches.

This is a job role: :job:`example-job`

This is a job variable role: :var:`example-job.foo.bar`

Roles
-----

.. role:: example-role

   This is an example role.

   **Role Variables**

   .. var:: foo

      This is a variable used by this role.

      .. var:: bar

         This is a sub key.

   .. var:: items
      :type: list

      This variable is a list.

      .. var:: baz

         This is an item in a list.

This is an (Ansible) role (Sphinx) role: :role:`example-role`

This is an (Ansible) role variable (Sphinx) role: :var:`example-role.items.baz`

Configuration Attributes
------------------------

.. attr:: example-attr
   :required:

   This is an example configuration attribute.

   .. attr:: foo
      :default: bar

      A sub attribute.

      .. value:: bar

         An attribute value.

      .. value:: baz

         Another attribute value.

This is an attribute role: :attr:`example-attr.foo`

This is an attribute value role: :value:`example-attr.foo.bar`


Job Variables
-------------

.. var:: example-variable

   This is an example variable.

   .. var:: foo

      This is a variable.

      .. var:: bar

         This is a sub key.

   .. var:: items
      :type: list

      This variable is a list.

      .. var:: baz

         This is an item in a list.

This is a variable role: :var:`example-variable.items.baz`


Statistics
----------

.. stat:: example-stat

   This is an example statistic.

   .. stat:: foo
      :type: counter

      A sub stat.

This is a statistics role: :stat:`example-stat.foo`
