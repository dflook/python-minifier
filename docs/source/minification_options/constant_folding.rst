Constant Folding
================

This transform evaluates constant expressions with literal operands when minifying and replaces the expression with the resulting value, if the value is shorter than the expression.

There are some limitations, notably the division and power operators are not evaluated.

This will be most effective with numeric literals.

This transform is always safe and enabled by default. Disable by passing the ``constant_folding=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-constant-folding`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: constant_folding.py

Output
~~~~~~

.. literalinclude:: constant_folding.min.py
    :language: python
