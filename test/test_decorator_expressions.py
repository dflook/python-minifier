import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_pep():
    if sys.version_info < (3, 9):
        pytest.skip('Decorator expression not allowed in python <3.9')

    source = """
buttons = [QPushButton(f'Button {i}') for i in range(10)]

# Do stuff with the list of buttons...

@buttons[0].clicked.connect
def spam():
    ...

@buttons[1].clicked.connect
def eggs():
    ...

# Do stuff with the list of buttons...
@(f, g)
def a(): pass

@(f, g)
class A:pass

@lambda func: (lambda *p: func(*p).u())
def g(n): pass

@s := lambda func: (lambda *p: func(*p).u())
def g(name): pass

@s
def r(n, t):
    pass

@lambda f: lambda *p: f or f(*p).u()
def g(name): pass

@lambda f: lambda *p: \
        [_ for _ in [ \
            f(*p),
            ] if _][0]
def c(): pass

@lambda f: lambda *p: \
            list(filter(lambda _: _,[
                (a := t()) and False,
                f(*p),
                (b := t()) and False,
            ]))[0]
def c(): pass

"""

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))
