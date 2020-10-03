import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_await_fstring():
    if sys.version_info < (3, 7):
        pytest.skip('Await in f-string expressions not allowed in python < 3.7')

    source = '''
async def a(): return 'hello'
async def b(): return f'{await b()}'
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))
