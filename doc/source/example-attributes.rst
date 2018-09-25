Configuration Attributes
------------------------

.. attr:: example-attr
   :required:

   This is an example configuration attribute.

   .. attr:: foo
      :default: bar
      :example: sample_value_for_example_attr
      :type: str

      A sub attribute.

      .. value:: bar

         An attribute value.

      .. value:: baz

         Another attribute value.

      .. attr:: moo

         An even further nested attribute

         .. attr:: boo

            And one more for good luck

.. attr:: another-example-attr

   And back to the top level

References
==========

This is an attribute role: :attr:`example-attr.foo`

This is an attribute value role: :value:`example-attr.foo.bar`

Summaries
=========

All attributes
^^^^^^^^^^^^^^

.. attr-overview::

Only one level
^^^^^^^^^^^^^^

.. attr-overview::
   :maxdepth: 1

Only example-attr.foo prefix
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. attr-overview::
   :prefix: example-attr.foo
