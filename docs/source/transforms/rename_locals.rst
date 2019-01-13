Rename Locals
=============

This transform shortens any non-global names.

This transform is almost always safe to use and enabled by default.

When enabled all non-global names may be renamed if it is space efficient and safe to do so. This includes:

  - Local variables
  - Functions in function scope
  - Classes in function scope
  - Local imports
  - Comprehension target names
  - Function arguments that are not typically referenced by the caller (`self`, `cls`, `args`, `kwargs`)
  - Function arguments may be bound with a new name in the function body, without changing the function signature
  - Exception handler target names

This will not change:

  - Global names
  - Names in class scope
  - Lambda function arguments (except args and kwargs)

New names are assigned according to the smallest minified result. To conserve the pool of available shortest names
they are reused in sibling namespaces and shadowed in child namespaces.

Disable this source transformation by passing the ``rename_locals=False`` argument to the :func:`python_minifier.minify`
function. The ``preserve_locals`` argument is a list of names to disable renaming for.

When using the pyminify command disable this transformation with ``--no-rename-locals``. The ``--preserve_locals`` option
may be a comma separated list of names to prevent renaming.

Use of some python builtins (``vars()``, ``exec()``, ``locals()``, ``globals()``, ``eval()``) in the minified module
will disable this transform, as it usually indicates usage of names that this transform can't recognise.

Example
-------

Input
~~~~~

.. literalinclude:: rename_locals.py

Output
~~~~~~

.. literalinclude:: rename_locals.min.py
    :language: python
