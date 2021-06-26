import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_dict_expanson():
    if sys.version_info < (3, 5):
        pytest.skip('dict expansion not allowed in python < 3.5')

    source = [
        r'{**a>>9}',
        r'{**(a or b)}',
        r'{**(a and b)}',
        r'{**a+b}',
        r'{**(lambda a:a)}',
        r'{**(a<b)}',
        r'{**(yield a())}',
        r'{**(a if a else a)}'
    ]

    for expression in source:
        expected_ast = ast.parse(expression)
        minified = unparse(expected_ast)
        compare_ast(expected_ast, ast.parse(minified))
        assert expression == minified
