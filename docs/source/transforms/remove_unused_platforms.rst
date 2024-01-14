Remove Unused Platforms
=======================

This transform removes ``if`` blocks that do not match a platform value.  This only supports
module level if blocks and is configured to keep a single explicit match.

The transform is disabled by default.

When using the API, enable it by either passing ``remove_unused_platforms=True``
argument to the :func:`python_minifier.minify`, or by passing ``remove_unused_platforms=unused_option``
to the function where unused_option is an instance of :class:`RemoveUnusedPlatformOptions`.

When using the pyminify command, enable it with ``--remove-unused-platforms`` and set the options
as required.

Options
-------

These arguments can be used with the pyminify command as shown by the following examples:

``--platform-test-key=_PLATFORM`` The variable name that is testing the platform

``--platform-preserve-value=linux`` The value that matches the target platform


Example
-------

Input
~~~~~

.. literalinclude:: remove_unused_platforms.py

Output
~~~~~~

.. literalinclude:: remove_unused_platforms.min.py
    :language: python
