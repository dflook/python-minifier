import ast
import sys

import pytest

from python_minifier import unparse
from python_minifier.ast_compare import compare_ast
from python_minifier.transforms.remove_explicit_return_none import RemoveExplicitReturnNone


def remove_return_none(source):
    module = ast.parse(source, 'remove_return_none')

    return RemoveExplicitReturnNone()(module)


def test_trailing_remove_return_none():
    source = 'def a():a=4;return None'
    expected = 'def a():a=4'

    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)

    assert unparse(actual_ast) == expected


def test_trailing_implicit_return_none():
    source = 'def a():a=4;return'
    expected = 'def a():a=4'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_trailing_remove_return_none_empty_suite():
    source = 'def a():return None'
    expected = 'def a():0'

    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)

    assert unparse(actual_ast) == expected


def test_trailing_implicit_return_none_empty_suite():
    source = 'def a():return'
    expected = 'def a():0'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_trailing_return_value_unchanged():
    source = 'def a():return 0'
    expected = source
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_remove_return_none():
    source = '''
def a():
    if a: return None
    return None
'''
    expected = 'def a():\n\tif a:return'

    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)

    assert unparse(actual_ast) == expected


def test_implicit_return_none():
    source = '''
def a():
    if a: return
    return
'''
    expected = 'def a():\n\tif a:return'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_return_value_unchanged():
    source = '''
def a():
    if a: return 1
    return 3
'''
    expected = 'def a():\n\tif a:return 1\n\treturn 3'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_async_trailing_remove_return_none():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = 'async def a():a=4;return None'
    expected = 'async def a():a=4'

    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)

    assert unparse(actual_ast) == expected


def test_async_trailing_implicit_return_none():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = 'async def a():a=4;return'
    expected = 'async def a():a=4'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_async_trailing_remove_return_none_empty_suite():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = 'async def a():return None'
    expected = 'async def a():0'

    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)

    assert unparse(actual_ast) == expected


def test_async_trailing_implicit_return_none_empty_suite():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = 'async def a():return'
    expected = 'async def a():0'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_async_trailing_return_value_unchanged():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = 'async def a():return 0'
    expected = source
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_async_remove_return_none():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = '''
async def a():
    if a: return None
    return None
'''
    expected = 'async def a():\n\tif a:return'

    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)

    assert unparse(actual_ast) == expected


def test_async_implicit_return_none():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = '''
async def a():
    if a: return
    return
'''
    expected = 'async def a():\n\tif a:return'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected


def test_async_return_value_unchanged():
    if sys.version_info < (3, 5):
        pytest.skip('Async not allowed in python < 3.5')

    source = '''
async def a():
    if a: return 1
    return 3
'''
    expected = 'async def a():\n\tif a:return 1\n\treturn 3'
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected
