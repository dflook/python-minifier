Remove Unused Imports
=====================

This transform removes imports of names that are never used.

An import statement is removed if none of the names it binds are used. If only some of the names are unused, just those
names are removed from the statement. A name is used if it is read anywhere in the module, including in nested
functions, decorators and default arguments.

This is not always safe, so the transform is disabled by default. It could break:

  - Any program that imports a name from the minified module, as nothing is known about how the module is used elsewhere
  - Imports that are only used for their side effects, like registering a codec
  - Names that are only referred to by strings, for example type annotations that are string literals or code run by ``getattr()``

Imports are never removed:

  - If ``eval()``, ``exec()``, ``locals()``, ``globals()``, ``vars()`` are used, or ``from <module> import *`` is used
    in the module
  - If they are ``__future__`` imports
  - If the name is included as a literal string in ``__all__`` at module level, or ``__all__`` is used in a way that
    can't be determined by looking at the module
  - If they are in a class body, where the names become attributes of the class

If an import statement is removed and a statement is still required, it is replaced by a zero expression statement.

Removing code can leave other code unused, so this transform is run again with the other dead code transforms until
there is nothing left to remove. For example if :doc:`remove_unused_definitions` removes a function, the imports that
were only used by that function are removed too.

Enable this source transformation by passing the ``remove_unused_imports=True`` argument to the :func:`python_minifier.minify`
function, or passing ``--remove-unused-imports`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_unused_imports.py

Output
~~~~~~

.. literalinclude:: remove_unused_imports.min.py
    :language: python
