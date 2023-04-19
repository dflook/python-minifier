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

'''
#(a:=B)
#a=(b:=c)
# foo(h:=6, x=(y := f(x)))
# def foo(answer=(p := 42)):pass
# def foo(answer: (p := 42) = 5, **asd:(c:=6)) -> (z:=1):pass
# a: (p := 42) = 5
# a += (b := 1)
# (x := lambda: 1)
# lambda: 1 +(x := 1) and 2
# lambda line: (m := re.match(pattern, line)) and m.group(1)
# f'{(x:=10)}'
# f'{x:=10}'
# with (x := await a, y := await b): pass
def test_named_expression_assignment_05(self):
    (x := 1, 2)
'''