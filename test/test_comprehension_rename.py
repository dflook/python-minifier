import ast
import sys

import pytest

from python_minifier import minify
from python_minifier.ast_compare import compare_ast

def test_listcomp_regression_2_7():
    if sys.version_info >= (3, 0):
        pytest.skip('ListComp doesn\'t create a new namespace in python < 3.0')

    source = '''
def f(pa):
    return [pa.b for pa in pa.c]
'''
    expected = source
    compare_ast(ast.parse(minify(source, rename_locals=True)), ast.parse(expected))

def test_listcomp_regression():
    if sys.version_info < (3, 0):
        pytest.skip('ListComp creates a new namespace in python > 3.0')

    source = '''
def f(parentObject):
    return [parentObject.b for parentObject in parentObject.c]
'''
    expected = '''
def f(parentObject):
    return[A.b for A in parentObject.c]
'''
    compare_ast(ast.parse(minify(source, rename_locals=True)), ast.parse(expected))


def test_expression():
    source = '''def test():
    [x*y for x in range(10) for y in range(x, x+10)]
'''

    expected = '''def test():
    [A*B for A in range(10) for B in range(A,A+10)]
'''
    compare_ast(ast.parse(minify(source, rename_locals=True)), ast.parse(expected))

def test_generator_expression():
    source = '''
x=1
def func():
    return (x for x in x)
'''

    expected = '''
x=1
def func():
    return (A for A in x)
'''

    compare_ast(ast.parse(minify(source, rename_locals=True)), ast.parse(expected))

def test_generator_expression_multiple_for():
    source = '''
def func():
    return (x for x in x for x in x)

def func(long_name, another_long_name):
    return (long_name for long_name, another_long_name in long_name for long_name in (long_name, another_long_name))
'''

    expected = '''
def func():
    return (A for A in x for A in A)

def func(long_name, another_long_name):
    return(A for A, B in long_name for A in (A,B))
'''

    compare_ast(ast.parse(minify(source, rename_locals=True)), ast.parse(expected))

def test_generator_expression_nested_for():
    source = '''
def func():
    return (a for a in (b for b in x) for c in c)

def func(long_name):
    return (a for a in (b for b in long_name) for c in c)
'''

    expected = '''
def func():
    return(A for A in (A for A in x) for B in B)

def func(long_name):
    return(A for A in (A for A in long_name) for B in B)
'''

    compare_ast(ast.parse(minify(source, rename_locals=True)), ast.parse(expected))
