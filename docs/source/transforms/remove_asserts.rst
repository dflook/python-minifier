Remove Asserts
==============

This transform removes assert statements.

Assert statements are evaluated by Python when it is not started with the `-O` option.
This transform is only safe to use if the minified output will by run with the `-O` option, or
you are certain that the assert statements are not needed.

If a statement is required, the assert statement will be replaced by a zero expression statement.

The transform is disabled by default. Enable it by passing the ``remove_asserts=True`` argument to the :func:`python_minifier.minify` function,
or passing ``--remove-asserts`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_asserts.py

Output
~~~~~~

.. literalinclude:: remove_asserts.min.py
    :language: python
