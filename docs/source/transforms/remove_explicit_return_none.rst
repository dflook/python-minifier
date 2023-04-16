Remove Explicit Return None
===========================

This transforms and ``return None`` statement into a ``return`` statement.
A return statement with no value is equivalent to ``return None``.

The transform is always safe to use and enabled by default. Disable by passing the ``remove_explicit_return_none=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-remove-explicit-remove-none`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_explicit_return_none.py

Output
~~~~~~

.. literalinclude:: remove_explicit_return_none.min.py
    :language: python
