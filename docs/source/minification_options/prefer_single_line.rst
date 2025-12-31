Prefer Single Line
==================

When minifying, statements at module level are separated by either newlines or semicolons. Both take the same number of bytes, so this option controls which is preferred.

When enabled, semicolons are used to keep multiple statements on a single line. When disabled (the default), newlines are used for slightly better readability of the minified output.

This option has no effect on the size of the output.

This option is disabled by default. Enable by passing the ``prefer_single_line=True`` argument to the :func:`python_minifier.minify` function,
or passing ``--prefer-single-line`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: prefer_single_line.py

Output with ``--prefer-single-line``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: prefer_single_line.min.py
    :language: python

Output without ``--prefer-single-line`` (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: prefer_single_line_false.min.py
    :language: python
