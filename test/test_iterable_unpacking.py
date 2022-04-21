import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_return_py38():
    if sys.version_info < (3, 8):
        pytest.skip('Parenthesis are always required in < 3.8')

    # Parenthesis are required
    source = 'def a():return(True,*[False])'

    expected_ast = ast.parse(source)
    minified = unparse(expected_ast, minimum_python_version=(3,0))
    compare_ast(expected_ast, ast.parse(minified))
    assert source == minified

    # Parenthesis not required
    source = 'def a():return True,*[False]'

    expected_ast = ast.parse(source)
    minified = unparse(expected_ast, minimum_python_version=(3,8))
    compare_ast(expected_ast, ast.parse(minified))
    assert source == minified


def test_return_py30():
    if sys.version_info < (3, 0):
        pytest.skip('Iterable unpacking in return not allowed in python < 3.0')

    # Parenthesis are required
    source = 'def a():return(True,*[False])'

    expected_ast = ast.parse(source)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert source == minified
