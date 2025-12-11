import ast

import pytest

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace, bind_names, resolve_names
from python_minifier.transforms.remove_debug import RemoveDebug


def remove_debug(source):
    module = ast.parse(source, 'remove_debug')

    add_parent(module)
    add_namespace(module)
    bind_names(module)
    resolve_names(module)
    return RemoveDebug()(module)


def test_remove_debug_empty_module():
    source = 'if __debug__: pass'
    expected = ''

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_debug_module():
    source = '''import collections
if __debug__: pass
a = 1
if __debug__: pass'''
    expected = '''import collections
a=1'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_if_empty():
    source = '''if True:
    if __debug__: pass'''
    expected = '''if True: 0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_suite():
    source = '''if True:
    if __debug__: pass
    a=1
    if __debug__: pass
    return None'''
    expected = '''if True:
    a=1
    return None'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_from_class():
    source = '''class A:
    if __debug__: pass
    a = 1
    if __debug__: pass
    def b():
        if __debug__: pass
        return 1
        if __debug__: pass
'''
    expected = '''class A:
    a=1
    def b():
        return 1
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_from_class_empty():
    source = '''class A:
    if __debug__: pass
'''
    expected = 'class A:0'

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_from_class_func_empty():
    source = '''class A:
    def b():
        if __debug__: pass
'''
    expected = '''class A:
    def b(): 0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


@pytest.mark.parametrize(
    'condition', [
        '__debug__',
        '__debug__ is True',
        '__debug__ is not False',
        '__debug__ == True'
    ]
)
def test_remove_truthy_debug(condition):
    source = '''
value = 10

# Truthy
if ''' + condition + ''':
  value += 1

print(value)
'''

    expected = '''
value = 10

print(value)
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


@pytest.mark.parametrize(
    'condition', [
        'not __debug__',
        '__debug__ is False',
        '__debug__ is not True',
        '__debug__ == False',
        'not __debug__ is True',
        'not __debug__ is not False',
        'not __debug__ == True'
    ]
)
def test_no_remove_falsy_debug(condition):
    source = '''
value = 10

# Truthy
if ''' + condition + ''':
  value += 1

print(value)
    '''

    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


@pytest.mark.parametrize(
    'condition', [
        '__sandwich__',
        '__sandwich__ is True',
        '__sandwich__ is False',
        '__sandwich__ is not False',
        '__sandwich__ == True',
        '__sandwich__ == __debug__',
        '__sandwich() == True',
        'func() is True',
        'some_call(a, b) is True',
        'obj.method() is True',
        'obj.attr is True',
        'True is something',
        'True == something',
    ]
)
def test_no_remove_not_debug(condition):
    source = '''
value = 10

# Not a __debug__ test
if ''' + condition + ''':
  value += 1

print(value)
    '''

    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)


def test_no_remove_is_true_in_elif_chain():
    """Regression test for issue #142 - if/elif/else with 'is True' comparisons"""
    source = '''
def check_is_internet_working(c):
    url, url_hostname = get_url_and_url_hostname(c)

    if is_internet_working_socket_test(c, url_hostname) is True:
        c.is_internet_connected = True
    elif is_internet_working_urllib_open(c, url) is True:
        c.is_internet_connected = True
    else:
        c.is_internet_connected = False

    return c.is_internet_connected
'''

    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_debug(source)
    compare_ast(expected_ast, actual_ast)
