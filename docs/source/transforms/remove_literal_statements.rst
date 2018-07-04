Remove Literal Statements
=========================

This transform removes statements that consist entirely of a literal value. This includes docstrings.
If a statement is required, it is replaced by a literal zero expression statement.

This transform will strip docstrings from the source. If the source module requires docstrings to remain in the
source, ensure this transform is disabled.

This transform is disabled by default. Enable by passing the ``remove_literal_statements=True`` argument to the :func:`python_minifier.minify` function,
or passing ``--remove_literal_statements`` to the pyminify command.

Examples
--------

Input
~~~~~

.. literalinclude:: remove_literal_statements.py

Output
~~~~~~

.. literalinclude:: remove_literal_statements.py.min
    :language: python
