"""
Test for renaming of local names

This assumes the standard NameAssigner and name_generator
"""

import ast
import sys

import pytest

from python_minifier import add_namespace, bind_names, resolve_names, allow_rename_locals, allow_rename_globals, \
    compare_ast, rename, CompareError, unparse


def rename_locals(source):

    # This will raise if the source file can't be parsed
    module = ast.parse(source, 'test_rename_locals')
    add_namespace(module)
    bind_names(module)
    resolve_names(module)

    allow_rename_locals(module, True)
    allow_rename_globals(module, False)

    rename(module)

    return module

def assert_code(expected_ast, actual_ast):
    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError as e:
        print(e)
        print(unparse(actual_ast))
        raise


def test_rename_variable_single_scope():
    source = '''
def a():
    a = 2
'''
    expected = '''
def a():
    A = 2
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_rename_multiple_definitions():
    source = '''
def inner(my_name):
    import collections as my_name
    def my_name(): pass
    my_name = 12
'''
    expected = '''
def inner(my_name):
    A=my_name
    import collections as A
    def A(): pass
    A = 12
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_rename_self_cls_in_place():
    source = '''
class TestClass():
    def mymethod(self): return self
    def mymethod2(qwertyuiop): return qwertyuiop
    def mymethod3(): return 'No Self'
    def mymethod4(self, a): return self, a

    @staticmethod
    def mystatic(cls): return cls
    @staticmethod    
    def mystatic(asdfghjkl): return asdfghjkl
    @staticmethod    
    def mystatic(): return 'No cls'
    
    @classmethod
    def mystatic(cls): return cls
    @classmethod    
    def mystatic(asdfghjkl): return asdfghjkl
    @classmethod    
    def mystatic(): return 'No cls'
    
    @unknown_decorator
    def unknown(self): return self
    @unknown_decorator    
    def unknown(qwertyuiop): return qwertyuiop
    @unknown_decorator        
    def unknown(self, arg): return self, arg
    @unknown_decorator    
    def unknown(): return 'No arg'        
    
'''
    expected = '''
class TestClass():
    def mymethod(A): return A
    def mymethod2(A): return A
    def mymethod3(): return 'No Self'
    def mymethod4(A, a): return A, a

    @staticmethod
    def mystatic(cls): return cls
    @staticmethod    
    def mystatic(asdfghjkl): return asdfghjkl
    @staticmethod    
    def mystatic(): return 'No cls'
    
    @classmethod
    def mystatic(A): return A
    @classmethod    
    def mystatic(A): return A
    @classmethod    
    def mystatic(): return 'No cls'
    
    @unknown_decorator
    def unknown(self): return self
    @unknown_decorator    
    def unknown(qwertyuiop): return qwertyuiop
    @unknown_decorator        
    def unknown(self, arg): return self, arg
    @unknown_decorator    
    def unknown(): return 'No arg'        
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)


def test_rename_arg_kwargs_in_place():
    source = '''
def test(arg, arg2, *args, **kwargs): return args, kwargs
def samename(arg, arg2, *asd, **asd): return asd
    
class TestClass():
    def mymethod(self, arg, *args, **kwargs): return args, kwargs
    
    @classmethod
    def mymethod(cls, arg, *args, **kwargs): return args, kwargs
'''
    expected = '''
def test(arg, arg2, *A, **B): return A, B
def samename(arg, arg2, *A, **A): return A
    
class TestClass():
    def mymethod(C, arg, *A, **B): return A, B
    
    @classmethod
    def mymethod(C, arg, *A, **B): return A, B   
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_no_rename_long_arg():
    source = '''
def f(this_is_my_long_argument_name):
    print(this_is_my_long_argument_name)
'''

    expected_ast = ast.parse(source)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)


def test_rename_long_arg():
    source = '''
def f(this_is_my_long_argument_name):
    print(this_is_my_long_argument_name)
    print(this_is_my_long_argument_name)    
'''
    expected = '''
def f(this_is_my_long_argument_name):
    A = this_is_my_long_argument_name
    print(A)
    print(A)
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_no_rename_single_char_arg():
    source = '''
def f(a):
    print(a)
    print(a)
    print(a)
    print(a) 
    print(a)  
    print(a) 
    print(a) 
    print(a) 
    print(a) 
    print(a) 
    print(a) 
    print(a) 
    print(a) 
    print(a) 
    print(a)                     
'''

    expected_ast = ast.parse(source)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_rename_arg():
    source = '''
def f(aa):
    print(aa)
    print(aa)
    print(aa)
    print(aa)
    print(aa)                           
'''
    expected = '''
def f(aa):
    A = aa
    print(A)
    print(A)
    print(A)
    print(A)
    print(A)                   
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_no_rename_lambda_arg():
    source = '''
lambda my_argument: f(my_argument + my_argument + my_argument)                       
'''

    expected_ast = ast.parse(source)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_rename_lambda_stararg():
    source = '''
lambda *args, **kwargs: f(args, kwargs)                       
'''

    expected = '''
lambda *A, **B: f(A, B)                       
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_python3_listcomp_scope():
    if sys.version_info < (3, 0):
        pytest.skip('No list comprehension scope in python < 3.0')

    source = '''
[a for a in mylist]                     
'''

    expected = '''
[A for A in mylist]                     
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_python2_listcomp_scope():
    if sys.version_info >= (3, 0):
        pytest.skip('list comprehension scope in python >= 3.0')

    source = '''
[a for a in mylist]               
def t():
    a = True
    [a for a in mylist] 
'''

    expected = '''
[a for a in mylist]               
def t():
    A = True
    [A for A in mylist]                    
'''

    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)

def test_arg_rename():

    source = '''
def f(*B,**A):pass
'''
    expected = '''
def f(*A,**B):pass
'''
    expected_ast = ast.parse(expected)
    actual_ast = rename_locals(source)
    assert_code(expected_ast, actual_ast)
