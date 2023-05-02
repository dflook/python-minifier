Remove Annotations
==================

This transform removes annotations. Although the annotations have no meaning to the python language,
they are made available at runtime. Some python library features require annotations to be kept.

Annotations can be removed from:

    - Function arguments
    - Function return
    - Variables
    - Class attributes

By default annotations are removed from variables, function arguments and function return, but not from class attributes.

This transform is generally safe to use with the default options. If you know the module requires the annotations to be kept, disable this transform.
Class attribute annotations can often be used by other modules, so it is recommended to keep them unless you know they are not used.

When removing class attribute annotations is enabled, annotations are kept for classes that are derived from:

    - dataclasses.dataclass
    - typing.NamedTuple
    - typing.TypedDict

If a variable annotation without assignment is used the annotation is changed to a literal zero instead of being removed.

Options
-------

These arguments can be used with the pyminify command:

``--no-remove-variable-annotations`` disables removing variable annotations

``--no-remove-return-annotations`` disables removing function return annotations

``--no-remove-argument-annotations`` disables removing function argument annotations

``--remove-class-attribute-annotations`` enables removing class attribute annotations

``--no-remove-annotations`` disables removing all annotations, this transform will not do anything.

When using the :func:`python_minifier.minify` function you can use the  ``remove_annotations`` argument to control this transform.
You can pass a boolean ``True`` to remove all annotations or a boolean ``False`` to keep all annotations.
You can also pass a :class:`python_minifier.transforms.remove_annotations.RemoveAnnotations` instance to specify which annotations to remove.

Example
-------

Input
~~~~~

.. literalinclude:: remove_annotations.py

Output
~~~~~~

.. literalinclude:: remove_annotations.min.py
    :language: python
