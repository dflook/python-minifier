import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_return():
    if sys.version_info < (3, 0):
        pytest.skip('Iterable unpacking in return not allowed in python < 3.0')

    elif sys.version_info < (3, 8):
        # Parenthesis are required
        source = 'def a():return(True,*[False])'

    else:
        # Parenthesis not required
        source = 'def a():return True,*[False]'

    expected_ast = ast.parse(source)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert source == minified
