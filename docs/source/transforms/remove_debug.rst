Remove Debug
============

This transform removes ``if`` statements that test ``__debug__`` is ``True``.

The builtin ``__debug__`` constant is True if Python is not started with the ``-O`` option.
This transform is only safe to use if the minified output will by run with the ``-O`` option, or
you are certain that any ``if`` statement that tests ``__debug__`` can be removed.

The condition is not evaluated. The statement is only removed if the condition exactly matches one of the forms in the example below.

If a statement is required, the ``if`` statement will be replaced by a zero expression statement.

The transform is disabled by default. Enable it by passing the ``remove_debug=True`` argument to the :func:`python_minifier.minify` function,
or passing ``--remove-debug`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_debug.py

Output
~~~~~~

.. literalinclude:: remove_debug.min.py
    :language: python
