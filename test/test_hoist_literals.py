import ast
import sys

import pytest

from python_minifier import unparse
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace, bind_names, resolve_names, rename, rename_literals, allow_rename_locals, allow_rename_globals

def hoist(source):
    module = ast.parse(source)
    add_namespace(module)
    bind_names(module)
    resolve_names(module)
    allow_rename_locals(module, False)
    allow_rename_globals(module, False)
    rename_literals(module)
    rename(module)
    print(unparse(module))
    return module

def test_nohoist_single_usage():
    source = '''
a = 'Hello'
'''

    expected = '''
a = 'Hello'
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_multiple_usage():
    source = '''
A = 'Hello'
B = 'Hello'
'''

    expected = '''
C = 'Hello'
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_no_hoist_multiple_small():
    source = '''
A = ''
B = ''
'''

    expected = '''
A = ''
B = ''
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_multiple_small():
    source = '''
A = '.'
B = '.'
C = '.'
D = '.'
E = '.'
F = '.'
G = '.'
'''

    expected = '''
H = '.'
A = H
B = H
C = H
D = H
E = H
F = H
G = H
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_insert_after_docstring():
    source = '''
"Hello this is a docstring"
import collections
A = 'Hello'
B = 'Hello'
'''

    expected = '''
"Hello this is a docstring"
C = 'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)


def test_hoist_insert_after_future():
    source = '''
from  __future__ import print_function
import collections
A = 'Hello'
B = 'Hello'
'''

    expected = '''
from __future__ import print_function
C = 'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_insert_after_future_docstring():
    source = '''
"Hello this is a docstring"
from  __future__ import print_function
import collections
A = 'Hello'
B = 'Hello'
'''

    expected = '''
"Hello this is a docstring"
from __future__ import print_function
C = 'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_bytes():
    source = '''
"Hello this is a docstring"
from  __future__ import print_function
import collections
A = b'Hello'
B = b'Hello'
'''

    expected = '''
"Hello this is a docstring"
from __future__ import print_function
C = b'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_after_multiple_future():
    source = '''
"Hello this is a docstring"
from __future__ import print_function
from __future__ import sausages
import collections
A = b'Hello'
B = b'Hello'
'''

    expected = '''
"Hello this is a docstring"
from __future__ import print_function
from __future__ import sausages
C = b'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_class():
    source = '''
class a:
    b = 'Hello'
    c = 'Hello'
'''

    expected = '''
A = 'Hello'
class a:
    b = A
    c = A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_from_class_to_func():
    source = '''
def z():
    class a:
        b = 'Hello'
        c = 'Hello'
'''

    expected = '''
def z():
    A = 'Hello'
    class a:
        b = A
        c = A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_from_func_to_func():
    source = '''
def z():
    def y():
        return 'Hello'
    def x():
        return 'Hello'
'''

    expected = '''
def z():
    A = 'Hello'
    def y():
        return A
    def x():
        return A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_in_func():
    source = '''
def z():
    def y():
        return 'Hello'
        return 'Hello'
'''

    expected = '''
def z():
    def y():
        A = 'Hello'
        return A
        return A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_over_class():
    source = '''
class a:
    def a():
        return 'Hello'
    def c():
        return 'Hello'
'''

    expected = '''
A = 'Hello'
class a:
    def a():
        return A
    def c():
        return A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_from_generator():
    source = '''
class a:
    def a():
        for i in (a for a in 'Hello'):
            pass
        for i in (a for a in 'World'):
            pass            
        return 'World'
    def c():
        return 'Hello'
'''

    expected = '''
A = 'Hello'
class a:
    def a():
        B = 'World'
        for i in (a for a in A):
            pass
        for i in (a for a in B):
            pass            
        return B
    def c():
        return A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_from_listcomp():
    source = '''
class a:
    def a():
        for i in [a for a in 'Hello']:
            pass
        for i in [a for a in 'World']:
            pass            
        return 'World'
    def c():
        return 'Hello'
'''

    expected = '''
A = 'Hello'
class a:
    def a():
        B = 'World'
        for i in [a for a in A]:
            pass
        for i in [a for a in B]:
            pass            
        return B
    def c():
        return A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)


def test_hoist_from_dictcomp():
    if sys.version_info < (2, 7):
        pytest.skip('No DictComp in python < 2.7')

    source = '''
class a:
    def a():
        for i in {a: a for a in 'Hello'}:
            pass
        for i in {a: a for a in 'World'}:
            pass            
        return 'World'
    def c():
        return 'Hello'
'''

    expected = '''
A = 'Hello'
class a:
    def a():
        B = 'World'
        for i in {a: a for a in A}:
            pass
        for i in {a: a for a in B}:
            pass            
        return B
    def c():
        return A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_from_setcomp():
    if sys.version_info < (2, 7):
        pytest.skip('No SetComp in python < 2.7')

    source = '''
class a:
    def a():
        for i in {a for a in 'Hello' + 'Hello' + 'World'}:
            pass
        return 'World'    
    def c():
        return 'World'
'''

    expected = '''
A = 'World'
class a:
    def a():
        B = 'Hello'
        for i in {a for a in B + B + A}:
            pass  
        return A
    def c():
        return A
'''

    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoist_from_lambda():
    source = '''
class a:
    def a():
        lambda: 'Hello' + 'Hello' + 'World'
    def c():
        return 'World'
'''

    expected = '''
A = 'World'
class a:
    def a():
        B = 'Hello'
        lambda: B + B + A
    def c():
        return A
'''
    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)

def test_hoisted_types_py3():
    if sys.version_info < (3, 0):
        pytest.skip('Python 3 only')

    source = '''
a = 'Hello' + 'Hello'
b = u'Hello' + u'Hello'
c = b'Hello' + b'Hello'
'''

    expected = '''
B = b'Hello'
A = 'Hello'
a = A + A
b = A + A
c = B + B
'''
    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)


def test_hoisted_types_py2():
    if sys.version_info >= (3, 0):
        pytest.skip('Python 2 only')

    source = '''
a = 'Hello' + 'Hello'
b = u'Hello' + u'Hello'
c = b'Hello' + b'Hello'
'''

    expected = '''
B = u'Hello'
A = 'Hello'
a = A + A
b = B + B
c = A + A
'''
    expected_ast = ast.parse(expected)
    actual_ast = hoist(source)
    compare_ast(expected_ast, actual_ast)
