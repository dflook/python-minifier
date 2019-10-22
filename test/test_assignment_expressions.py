import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_pep():
    if sys.version_info < (3, 8):
        pytest.skip('No Assignment expressions in python < 3.8')

    source = '''
if a := True:
    print(a)
if self._is_special and (ans := self._check_nans(context=context)):
    return ans    
results = [(x, y, x/y) for x in input_data if (y := f(x)) > 0]
stuff = [[y := f(x), x/y] for x in range(5)]    
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))
