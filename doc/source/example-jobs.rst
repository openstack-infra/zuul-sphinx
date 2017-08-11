Example Jobs
============

Jobs
----

.. job:: example

   This is an example job.

   .. jobvar:: foo

      This is a variable used by this job.

      .. jobvar:: bar
         :default: zero

         This is a sub key.

   .. jobvar:: items
      :type: list

      This variable is a list.

      .. jobvar:: baz

         This is an item in a list.

.. job:: example
   :variant: stable

   This is a variant of :job:`example` which runs on stable branches.

This is a job role: :job:`example`

This is a job variable role: :jobvar:`example.foo.bar`
