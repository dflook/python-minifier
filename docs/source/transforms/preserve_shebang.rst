Preserve Shebang
================

The shebang line indicates what interpreter should be used by the operating system when loading a python file as an executable.
It does not have any meaning to python itself, but may be needed if python files should be directly executable.

When this option is enabled, any shebang line is preserved in the minified output. The option is enabled by default.

Disable this option by passing ``preserve_shebang=False`` to the :func:`python_minifier.minify` function,
or passing ``--no-preserve-shebang`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: preserve_shebang.py

Output
~~~~~~

.. literalinclude:: preserve_shebang.min.py
    :language: python
