import ast

from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_slice():
    """AST for slices was changed in 3.9"""

    source = '''
x[name]
x[1:2]
x[1:2, 3]
x[()]
x[1:2, 2:2]
x[a, ..., b:c]
x[a, ..., b]
x[(a, b)]
x[a:b,]
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))
