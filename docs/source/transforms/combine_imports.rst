Combine Imports
===============

This transform combines adjacent import statements into a single statement.
The order of the imports will not be changed.
This transform is always safe to use and enabled by default.

Disable this source transformation by passing the ``combine_imports=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-combine-imports`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: combine_imports.py

Output
~~~~~~

.. literalinclude:: combine_imports.min.py
    :language: python
