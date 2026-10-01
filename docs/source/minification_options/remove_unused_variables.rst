Remove Unused Variables
=======================

This transform removes assignments to variables that are never used.

An assignment is removed if the name is not used anywhere in the module, and evaluating the assigned value is known not
to have any effect. Assigning a literal, a collection of literals, a name, an attribute, a subscript, a lambda,
or an expression made of operators with these is removed. Anything that calls a function, uses ``await`` or ``yield``,
or is a comprehension is kept, as is any value that might unpack an iterable or mapping.

Only assignments that bind a single name are removed, including annotated assignments with a value.
Assignments to attributes and subscripts, to multiple targets, and augmented assignments are always kept.
Using a name with ``del``, an augmented assignment or ``global`` and ``nonlocal`` declarations all count as a use.

This is not always safe, so the transform is disabled by default. It could break any program that imports a
variable from the minified module, or reads variables by a string name. Reading an attribute or subscript, and applying
an operator, are assumed to have no effect, but they may run code that does.

Assignments are never removed:

  - If ``eval()``, ``exec()``, ``locals()``, ``globals()``, ``vars()`` are used, or ``from <module> import *`` is used
    in the module
  - If the name is a dunder name like ``__version__``
  - If the name is included as a literal string in ``__all__`` at module level, or ``__all__`` is used in a way that
    can't be determined by looking at the module
  - If they are in a class body, where the names become attributes of the class

If an assignment is removed and a statement is still required, it is replaced by a zero expression statement.

Removing code can leave other code unused, so this transform is run again with the other dead code transforms until
there is nothing left to remove.

Enable this source transformation by passing the ``remove_unused_variables=True`` argument to the :func:`python_minifier.minify`
function, or passing ``--remove-unused-variables`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_unused_variables.py

Output
~~~~~~

.. literalinclude:: remove_unused_variables.min.py
    :language: python
