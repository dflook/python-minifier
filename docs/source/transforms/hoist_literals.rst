Hoist Literals
==============

This transform replaces string and bytes literals with references to module level variables.
This will only be done if multiple literals can be replaced with a single variable referenced in
multiple locations (and the resulting code is smaller).

If ``from <module> import *`` is used, this module has no effect. Without knowing the names imported into
the module, we can't safely give names to the new variables.

This transform is always safe to use and enabled by default.
Disable this source transformation by passing the ``hoist_literals=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-hoist-literals`` to the pyminify command.

Examples
--------

Input
~~~~~

.. literalinclude:: hoist_literals.py

Output
~~~~~~

.. literalinclude:: hoist_literals.py.min
    :language: python
