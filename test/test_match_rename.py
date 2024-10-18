import ast
import sys

import pytest

from python_minifier import unparse
from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import CompareError, compare_ast
from python_minifier.rename import (
    add_namespace,
    allow_rename_globals,
    allow_rename_locals,
    bind_names,
    rename,
    rename_literals,
    resolve_names
)


def do_rename(source, allow_locals, allow_globals):
    # This will raise if the source file can't be parsed
    module = ast.parse(source, 'test_match_rename')
    add_parent(module)
    add_namespace(module)
    bind_names(module)
    resolve_names(module)

    allow_rename_locals(module, allow_locals)
    allow_rename_globals(module, allow_globals)

    rename_literals(module)
    rename(module)

    return module


def assert_code(expected_ast, actual_ast):
    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError as e:
        print(e)
        print(unparse(actual_ast))
        raise


def test_rename_subject_global():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
match hello + hello + hello + hello:
  case hello: pass

def func():
    match hello + hello + hello + hello:
      case hello: pass

match 'hello' + 'hello':
  case 'hello': pass
'''
    expected = '''
B='hello'
match A + A + A + A:
  case A: pass

def C():
    match hello + hello + hello + hello:
      case hello: pass

match B + B:
  case 'hello': pass
'''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=False, allow_globals=True)
    assert_code(expected_ast, actual_ast)


def test_rename_subject_locals():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
match hello + hello + hello + hello:
    case hello: pass

def func(expensive_rename):
    match hello + hello + hello + hello:
        case hello: pass

    match expensive_rename:
        case None: pass

    match 'hello' + 'hello' + 'hello':
        case 'hello': pass
'''
    expected = '''
match hello + hello + hello + hello:
  case hello: pass

def func(expensive_rename):
    B='hello'
    match A + A + A + A:
        case A: pass

    match expensive_rename:
        case None: pass

    match B + B + B:
        case 'hello': pass
'''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=True, allow_globals=False)
    assert_code(expected_ast, actual_ast)


def test_rename_guard_local():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
match None:
    case None if sausage + sausage + sausage + sausage: pass

def func(expensive_rename):
    hello=0
    match None:
        case None if hello + hello + hello + hello: pass
        case None if expensive_rename: pass
        case 'hello' if 'hello' + 'hello' + 'hello' + 'hello': pass
    '''
    expected = '''
match None:
    case None if sausage + sausage + sausage + sausage: pass

def func(expensive_rename):
    B='hello'
    A=0
    match None:
        case None if A + A + A + A: pass
        case None if expensive_rename: pass
        case 'hello' if B + B + B + B: pass
    '''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=True, allow_globals=False)
    assert_code(expected_ast, actual_ast)


def test_rename_guard_global():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
sausage=0
match None:
    case None if sausage + sausage + sausage + sausage: pass
    case 'hello' if 'hello' + 'hello' + 'hello' + 'hello': pass

def func(expensive_rename):
    hello=0
    match None:
        case None if hello + hello + hello + hello: pass
        case None if expensive_rename: pass
        case 'hello' if 'hello' + 'hello' + 'hello' + 'hello': pass
        '''

    expected = '''
A='hello'
B=0
match None:
    case None if B + B + B + B: pass
    case 'hello' if A + A + A + A: pass

def C(expensive_rename):
    hello=0
    match None:
        case None if hello + hello + hello + hello: pass
        case None if expensive_rename: pass
        case 'hello' if A + A + A + A: pass
        '''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=False, allow_globals=True)
    assert_code(expected_ast, actual_ast)


def test_rename_body_local():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
sausage=0
match None:
    case None: sausage + sausage + sausage + sausage

def func(expensive_rename):
    hello=0
    match None:
        case None: hello + hello + hello + hello
        case None: expensive_rename
        '''

    expected = '''
sausage=0
match None:
    case None: sausage + sausage + sausage + sausage

def func(expensive_rename):
    A=0
    match None:
        case None: A + A + A + A
        case None: expensive_rename
        '''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=True, allow_globals=False)
    assert_code(expected_ast, actual_ast)


def test_rename_body_global():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
sausage=0
match None:
    case None: sausage + sausage + sausage + sausage

def func(expensive_rename):
    hello=0
    match None:
        case None: hello + hello + hello + hello
        case None: expensive_rename
        '''

    expected = '''
A=0
match None:
    case None: A + A + A + A

def B(expensive_rename):
    hello=0
    match None:
        case None: hello + hello + hello + hello
        case None: expensive_rename
        '''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=False, allow_globals=True)
    assert_code(expected_ast, actual_ast)


def test_rename_pattern_local():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
class Global: pass

match None:
    case expensive_rename(q, w) if q: w
    case Global(u, i) if u: i
    case ['hello', 'hello', 'hello', 'hello']: pass
    case [None, None, None, None]: pass
    case [True, True, True, True]: pass
    case [False, False, False, False]: pass

def func(expensive_rename):
    class Local: pass

    match None:
        case expensive_rename(a, b) if a: b
        case Global(d, e) if d: e
        case Local(f, g) if f: g
        case ['hello', 'hello', 'hello', 'hello']: pass
        case [None, None, None, None]: pass
        case [True, True, True, True]: pass
        case [False, False, False, False]: pass
            '''

    expected = '''
class Global: pass

match None:
    case expensive_rename(q, w) if q: w
    case Global(u, i) if u: i
    case ['hello', 'hello', 'hello', 'hello']: pass
    case [None, None, None, None]: pass
    case [True, True, True, True]: pass
    case [False, False, False, False]: pass

def func(expensive_rename):
    class A: pass

    match None:
        case expensive_rename(B, C) if B: C
        case Global(D, E) if D: E
        case A(F, G) if F: G
        case ['hello', 'hello', 'hello', 'hello']: pass
        case [None, None, None, None]: pass
        case [True, True, True, True]: pass
        case [False, False, False, False]: pass
            '''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=True, allow_globals=False)
    assert_code(expected_ast, actual_ast)


def test_rename_pattern_global():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
class Global: pass

match None:
    case Global(u, i) if u: i
    case ['hello', 'hello', 'hello', 'hello']: pass
    case [None, None, None, None]: pass
    case [True, True, True, True]: pass
    case [False, False, False, False]: pass

def func(expensive_rename):
    class Local: pass

    match None:
        case expensive_rename(a, b) if a: b
        case Global(d, e) if d: e
        case Local(f, g) if f: g
        case ['hello', 'hello', 'hello', 'hello']: pass
        case [None, None, None, None]: pass
        case [True, True, True, True]: pass
        case [False, False, False, False]: pass
                '''

    expected = '''
class A: pass

match None:
    case A(B, C) if B: C
    case ['hello', 'hello', 'hello', 'hello']: pass
    case [None, None, None, None]: pass
    case [True, True, True, True]: pass
    case [False, False, False, False]: pass

def D(expensive_rename):
    class Local: pass

    match None:
        case expensive_rename(a, b) if a: b
        case A(d, e) if d: e
        case Local(f, g) if f: g
        case ['hello', 'hello', 'hello', 'hello']: pass
        case [None, None, None, None]: pass
        case [True, True, True, True]: pass
        case [False, False, False, False]: pass
                '''

    expected_ast = ast.parse(expected)
    actual_ast = do_rename(source, allow_locals=False, allow_globals=True)
    assert_code(expected_ast, actual_ast)
