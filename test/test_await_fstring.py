import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_await_fstring():
    if sys.version_info < (3, 6):
        pytest.skip('No f-string expressions in python < 3.6')

    source = '''
f'{await 0}'
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))
