Examples
========

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
