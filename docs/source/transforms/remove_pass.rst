Remove Pass
===========

This transform removes pass statements. If a statement is required,
it is replaced by a literal zero expression statement.

This transform is always safe to use and enabled by default.

Disable this source transformation by passing the ``remove_pass=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-remove-pass`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_pass.py

Output
~~~~~~

.. literalinclude:: remove_pass.min.py
    :language: python
