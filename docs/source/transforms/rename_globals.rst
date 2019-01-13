Rename Globals
==============

This transform shortens names in the module scope. This includes introducing short names for builtins.

This could break any program that imports the minified module. For this reason the transform is disabled by
default.

When enabled, all global names may be renamed if it is space efficient. This includes:

  - Global variables
  - Global import aliases
  - Global function names
  - Global class names
  - Builtin names may be bound to a new name in the module scope

Renaming is prevented by:

  - If ``eval()``, ``exec()``, ``locals()``, ``globals()``, ``vars()`` are used, renaming is disabled
  - If ``from <module> import *`` is used in the module, renaming is disabled
  - If a name is included as a literal string in ``__all__``, renaming of that name is disabled
  - Any name listed in the ``preserve_globals`` argument

Enable this source transformation by passing the ``rename_globals=True`` argument to the :func:`python_minifier.minify`
function. The ``preserve_globals`` argument is a list of names to disable renaming for.

When using the pyminify command enable this transformation with ``--rename-globals``. The ``--preserve_globals`` option
may be a comma separated list of names to prevent renaming.

Example
-------

Input
~~~~~

.. literalinclude:: rename_globals.py

Output
~~~~~~

.. literalinclude:: rename_globals.min.py
    :language: python
