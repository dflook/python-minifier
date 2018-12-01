"""
Test for renaming of builtins

This assumes the standard NameAssigner and name_generator
"""

import ast
import sys

import pytest

from python_minifier import add_namespace, bind_names, resolve_names, allow_rename_locals, allow_rename_globals, \
    compare_ast, rename, CompareError, unparse


def do_rename(source):
    # This will raise if the source file can't be parsed
    module = ast.parse(source, 'test_rename_bultins')
    add_namespace(module)
    bind_names(module)
    resolve_names(module)

    allow_rename_locals(module, True)
    allow_rename_globals(module, True)

    rename(module)

    return module


def assert_code(expected_ast, actual_ast):
    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError as e:
        print(e)
        print(unparse(actual_ast))
        raise


def test_rename_builtins():
    source = '''
sorted()
sorted()
sorted()
sorted()
sorted()
'''
    expected = '''
A=sorted
A()
A()
A()
A()
A()
'''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source)
    assert_code(expected_ast, actual_ast)


def test_no_rename_assigned_builtin():
    source = '''
if random.choice([True, False]):
    sorted=str
sorted()
sorted()
sorted()
sorted()
sorted()
'''
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source)
    assert_code(expected_ast, actual_ast)

def test_rename_local_builtin():
    source = '''
def t():
    sorted()
    sorted()
    sorted()
    sorted()
    sorted()
'''
    expected = '''
A=sorted
def B():
    A()
    A()
    A()
    A()
    A()
'''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source)
    assert_code(expected_ast, actual_ast)

def test_no_rename_local_assigned_builtin():
    source = '''
def a():
    if random.choice([True, False]):
        sorted=str
    sorted()
    sorted()
    sorted()
    sorted()
    sorted()
'''

    expected = '''
def A():
    if random.choice([True, False]):
        sorted=str
    sorted()
    sorted()
    sorted()
    sorted()
    sorted()
'''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source)
    assert_code(expected_ast, actual_ast)
