Remove Literal Statements
=========================

This transform removes statements that consist entirely of a literal value, which can include docstrings.

'Literal statements' are statements that consist entirely of a literal value, i.e string, bytes, number, ellipsis, True, False or None.
These statements have no effect on the program and can be removed.
There is one common exception to this, which is docstrings. A string literal that is the first statement in module, function or class is a docstring.
Docstrings are made available to the program at runtime, so could affect it's behaviour if removed.

This transform has separate options to configure removal of literal statements:

    - Remove module docstring
    - Remove function docstrings
    - Remove class docstrings
    - Remove any other literal statements

If a literal can be removed but a statement is required, it is replaced by a literal zero expression statement.

If it looks like docstrings are used by the module they will not be removed regardless of the options.
If the module uses the ``__doc__`` name the module docstring will not be removed.
If a ``__doc__`` attribute is used in the module, docstrings will not be removed from functions or classes.

By default this transform will remove all literal statements except docstrings.

Options
-------

These arguments can be used with the pyminify command:

``--remove-module-docstring`` removes the module docstring if it is not used.

``--remove-function-docstrings`` removes function docstrings if they are not used.

``--remove-class-docstrings`` removes class docstrings if they are not used.

``--no-remove-literal-expression-statements`` disables removing non-docstring literal statements.

``--remove-literal-statements`` is an alias for ``--remove-module-docstring --remove-function-docstrings --remove-class-docstrings``.

When using the :func:`python_minifier.minify` function you can use the  ``remove_literal_statements`` argument to control this transform.
You can pass a boolean ``True`` to remove all literal statements (including docstrings) or a boolean ``False`` to not remove any.
You can also pass a :class:`python_minifier.RemoveLiteralStatementsOptions` instance to specify what to remove

Example
-------

Input
~~~~~

.. literalinclude:: remove_literal_statements.py

Output
~~~~~~

.. literalinclude:: remove_literal_statements.min.py
    :language: python
