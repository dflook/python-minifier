Remove Builtin Exception Brackets
=================================

This transform removes parentheses when raising builtin exceptions with no arguments.

The raise statement automatically instantiates exceptions with no arguments, so the parentheses are unnecessary.
This transform does nothing on Python 2.

If the exception is not a builtin exception, or has arguments, the parentheses are not removed.

This transform is enabled by default. Disable by passing the ``remove_builtin_exception_brackets=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-remove-builtin-exception-brackets`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_exception_brackets.py

Output
~~~~~~

.. literalinclude:: remove_exception_brackets.min.py
    :language: python
