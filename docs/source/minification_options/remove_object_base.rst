Remove Object Base
==================

In Python 3 all classes implicitly inherit from ``object``. This transform removes ``object`` from the base class list
of all classes. This transform does nothing on Python 2.

This transform is always safe to use and enabled by default.

Disable this source transformation by passing the ``remove_object_base=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-remove-object-base`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_object_base.py

Output
~~~~~~

.. literalinclude:: remove_object_base.min.py
    :language: python
