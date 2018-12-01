Hoist Literals
==============

This transform replaces string and bytes literals with references to module level variables.
It may also introduce new names for some builtin constants (True, False, None).
This will only be done if multiple literals can be replaced with a single variable referenced in
multiple locations (and the resulting code is smaller).

If the rename_globals transform is disabled, the newly introduced names have an underscore prefix.

This transform is always safe to use and enabled by default.
Disable this source transformation by passing the ``hoist_literals=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-hoist-literals`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: hoist_literals.py

Output
~~~~~~

.. literalinclude:: hoist_literals.min.py
    :language: python
