Remove Unused Definitions
=========================

This transform removes functions and classes that are never used.

A function or class definition is removed if its name is not used anywhere in the module. Methods and the other names
defined in a class body are never removed, only functions and classes defined at module level or inside a function.

A definition is kept if executing it could have an effect, which is when:

  - It has a decorator, as the decorator may register the function or class somewhere
  - A default value, annotation, base class or keyword evaluates something that isn't known to be harmless, like a call
  - The body of a class runs anything that isn't a simple assignment, a docstring or a definition

This is not always safe, so the transform is disabled by default. It could break any program that imports a
definition from the minified module, or looks up definitions by a string name. A class without a decorator could
still be registered by a base class or metaclass.

Definitions are never removed:

  - If ``eval()``, ``exec()``, ``locals()``, ``globals()``, ``vars()`` are used, or ``from <module> import *`` is used
    in the module
  - If the name is a dunder name like ``__getattr__``
  - If the name is included as a literal string in ``__all__`` at module level, or ``__all__`` is used in a way that
    can't be determined by looking at the module

If a definition is removed and a statement is still required, it is replaced by a zero expression statement.

Removing code can leave other code unused, so this transform is run again with the other dead code transforms until
there is nothing left to remove. For example removing a function also removes any helper that only that function used.

Enable this source transformation by passing the ``remove_unused_definitions=True`` argument to the :func:`python_minifier.minify`
function, or passing ``--remove-unused-definitions`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_unused_definitions.py

Output
~~~~~~

.. literalinclude:: remove_unused_definitions.min.py
    :language: python
