"""
This should pass typechecking
"""

import ast

from python_minifier import minify, unparse, awslambda, RemoveAnnotationsOptions

def test_typing() -> None:
    """ This should have good types """

    unparse(ast.parse('pass'))
    minify('pass')
    minify(b'pass')
    minify('pass',
           filename='filename',
           remove_annotations=True,
           remove_pass=True,
           remove_literal_statements=False,
           combine_imports=True,
           hoist_literals=True,
           rename_locals=True,
           preserve_locals=None,
           rename_globals=False,
           preserve_globals=None,
           remove_object_base=True,
           convert_posargs_to_args=True,
           preserve_shebang=True,
           remove_asserts=True,
           remove_debug=True
    )
    awslambda('pass')
    awslambda('pass',
              filename='filename',
              entrypoint='myentrypoint'
    )

    annotation_options = RemoveAnnotationsOptions(
        remove_variable_annotations=True,
        remove_return_annotations=True,
        remove_argument_annotations=True,
        remove_class_attribute_annotations=False
    )
    minify('pass', remove_annotations=annotation_options)
