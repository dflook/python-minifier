Remove Dead Branches
====================

This transform removes ``if`` statement branches that can never run because the condition is a constant.

An ``if`` statement with a constant ``False`` condition is removed, keeping its ``else`` branch. An ``if`` statement
with a constant ``True`` condition is replaced by its body, dropping any ``else`` branch. Only the literals ``True``
and ``False`` are treated as constants; the condition is not otherwise evaluated, so a name such as ``DEBUG`` is left
alone even if it was assigned a constant value.

A branch is only removed when doing so does not change the meaning of the program. A branch is kept if removing it
would change the enclosing scope, for example if it contains a ``yield``, a ``global`` or ``nonlocal`` declaration, or
the only assignment to a local variable. At module and class scope, where name resolution is dynamic, unreachable
assignments and imports are removed.

If a branch is removed and a statement is still required, it is replaced by a zero expression statement.

This transform also removes the ``if __debug__`` branches marked by the :doc:`remove_debug` transform, so enabling
that transform requires this one to remain enabled.

This transform is safe and enabled by default. Disable it by passing the ``remove_dead_branches=False`` argument to the
:func:`python_minifier.minify` function, or passing ``--no-remove-dead-branches`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_dead_branches.py

Output
~~~~~~

.. literalinclude:: remove_dead_branches.min.py
    :language: python
