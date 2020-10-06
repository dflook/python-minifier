Convert Positional-Only Argument to Arguments
=============================================

This transform converts positional-only arguments into normal arguments by removing the '/' separator in the
argument list.

This transform is almost always safe to use and enabled by default.

Disable this source transformation by passing the ``convert_posargs_to_args=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-convert-posargs-to-args`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: convert_posargs_to_args.py

Output
~~~~~~

.. literalinclude:: convert_posargs_to_args.min.py
    :language: python
