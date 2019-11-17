import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast
from python_minifier.transforms.remove_posargs import remove_posargs

def test_pep():
    if sys.version_info < (3, 8):
        pytest.skip('No Assignment expressions in python < 3.8')

    source = '''
def name(p1, p2, /, p_or_kw, *, kw): pass
def name(p1, p2=None, /, p_or_kw=None, *, kw): pass
def name(p1, p2=None, /, *, kw): pass
def name(p1, p2=None, /): pass
def name(p1, p2, /, p_or_kw): pass
def name(p1, p2, /): pass
def name(p_or_kw, *, kw): pass
def name(*, kw): pass

def standard_arg(arg):
    print(arg)
def pos_only_arg(arg, /):
    print(arg)
def kwd_only_arg(*, arg):
    print(arg)
def combined_example(pos_only, /, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_convert():
    if sys.version_info < (3, 8):
        pytest.skip('No Assignment expressions in python < 3.8')

    source = '''
def name(p1, p2, /, p_or_kw, *, kw): pass
def name(p1, p2=None, /, p_or_kw=None, *, kw): pass
def name(p1, p2=None, /, *, kw): pass
def name(p1, p2=None, /): pass
def name(p1, p2, /, p_or_kw): pass
def name(p1, p2, /): pass
def name(p_or_kw, *, kw): pass
def name(*, kw): pass

def standard_arg(arg):
    print(arg)
def pos_only_arg(arg, /):
    print(arg)
def kwd_only_arg(*, arg):
    print(arg)
def combined_example(pos_only, /, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)
'''

    expected = '''
def name(p1, p2, p_or_kw, *, kw): pass
def name(p1, p2=None, p_or_kw=None, *, kw): pass
def name(p1, p2=None, *, kw): pass
def name(p1, p2=None): pass
def name(p1, p2, p_or_kw): pass
def name(p1, p2): pass
def name(p_or_kw, *, kw): pass
def name(*, kw): pass

def standard_arg(arg):
    print(arg)
def pos_only_arg(arg):
    print(arg)
def kwd_only_arg(*, arg):
    print(arg)
def combined_example(pos_only, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)
'''

    expected_ast = ast.parse(expected)
    actual_ast = unparse(remove_posargs(ast.parse(source)))
    compare_ast(expected_ast, ast.parse(actual_ast))