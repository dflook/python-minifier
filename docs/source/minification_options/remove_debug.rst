Remove Debug
============

This transform removes ``if`` statements that test ``__debug__`` is ``True``.

The builtin ``__debug__`` constant is True if Python is not started with the ``-O`` option.
This transform is only safe to use if the minified output will be run with the ``-O`` option, or
you are certain that any ``if`` statement that tests ``__debug__`` can be removed.

The condition is not evaluated. A statement is only affected if the condition exactly matches one of the truthy forms
in the example below.

The removal is performed by the :doc:`remove_dead_branches` transform, which this transform marks the ``if`` statements
for. That transform must remain enabled (it is by default) for this option to have any effect, and it will keep a branch
that cannot be removed without changing the meaning of the program. If a branch is removed and a statement is still
required, it is replaced by a zero expression statement.

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
