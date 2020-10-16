Remove Annotations
==================

This transform removes function annotations and variable annotations.

This transform is generally safe to use. Although the annotations have no meaning to the python language,
they are made available at runtime. Some python library features require annotations to be kept.

If these are detected, annotations are kept for that class:

    - dataclasses.dataclass
    - typing.NamedTuple
    - typing.NamedDict

If you know the module requires the annotations to be kept, disable this transform.

If a variable annotation without assignment is used the annotation is changed to a literal zero instead of being removed.

The transform is enabled by default.
Disable this source transformation by passing the ``remove_annotations=False`` argument to the :func:`python_minifier.minify` function,
or passing ``--no-remove-annotations`` to the pyminify command.

Example
-------

Input
~~~~~

.. literalinclude:: remove_annotations.py

Output
~~~~~~

.. literalinclude:: remove_annotations.min.py
    :language: python
