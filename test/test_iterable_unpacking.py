import ast
import sys
import pytest
from python_minifier import unparse, TargetPythonOptions
from python_minifier.ast_compare import compare_ast

def test_required_parens():
    if sys.version_info < (3, 0):
        pytest.skip('Iterable unpacking in return not allowed in python < 3.0')

    if sys.version_info > (3, 7):
        pytest.skip('Parens not required in python > 3.7')

    # Parenthesis are required
    source = 'def a():return(True,*[False])'

    expected_ast = ast.parse(source)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert source == minified

def test_target_required_parens():
    if sys.version_info < (3, 8):
        pytest.skip('Parens always required in python < 3.8')

    source = 'def a():return True,*[False]'
    with_parens = 'def a():return(True,*[False])'

    expected_ast = ast.parse(source)

    # Without constraining the python version, compatibility is assumed to be down to 3.0, so use parens

    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert with_parens == minified

    # When constraining to min python >= 3.8, parens are not required
    python_38_minimum = TargetPythonOptions((3, 8), (sys.version_info.major, sys.version_info.minor))
    minified = unparse(expected_ast, target_python=python_38_minimum)
    compare_ast(expected_ast, ast.parse(minified))
    assert source == minified
