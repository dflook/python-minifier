Remove Unreachable
==================

This transform removes statements that follow a statement that always leaves the block it is in.

The statements after a ``return``, ``raise``, ``break`` or ``continue`` in the same block are removed, as they can never
run. The same is true for the statements after an ``if`` statement where every branch ends this way, so it needs an
``else`` clause. A ``try`` statement ends the block if its ``finally`` clause does, or if its body and all of its
``except`` clauses do. A ``with`` statement ends the block if its body does, unless it only does so by raising
an exception, as the context manager may suppress that. ``for`` and ``while`` loops never end the block, as their body
might not run.

The statements are kept if removing them would change the meaning of the program, for example if they contain a ``yield``,
a ``global`` or ``nonlocal`` declaration, or the only assignment to a local variable that is used before it.

If ``eval()``, ``exec()``, ``locals()``, ``globals()``, ``vars()`` are used, or ``from <module> import *`` is used
in the module, nothing is removed.

Removing code can leave other code unused, so this transform is run again with the other dead code transforms until
there is nothing left to remove. For example the names that were only used by unreachable statements may be removed
by :doc:`remove_unused_imports`.

The transform is disabled by default. Enable it by passing the ``remove_unreachable=True`` argument to the :func:`python_minifier.minify` function,
or passing ``--remove-unreachable`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_unreachable.py

Output
~~~~~~

.. literalinclude:: remove_unreachable.min.py
    :language: python
