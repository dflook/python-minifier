import ast

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace, bind_names, resolve_names
from python_minifier.transforms.remove_asserts import RemoveAsserts


def remove_asserts(source):
    module = ast.parse(source, 'remove_asserts')

    add_parent(module)
    add_namespace(module)
    bind_names(module)
    resolve_names(module)
    return RemoveAsserts()(module)


def test_remove_assert_empty_module():
    source = 'assert False'
    expected = ''

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_assert_module():
    source = '''import collections
assert False
a = 1
assert False'''
    expected = '''import collections
a=1'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_if_empty():
    source = '''if True:
    assert False'''
    expected = '''if True:
    0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_if_line():
    source = '''if True: assert False'''
    expected = '''if True: 0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_suite():
    source = '''if True:
    assert False
    a=1
    assert False
    return None'''
    expected = '''if True:
    a=1
    return None'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_from_class():
    source = '''class A:
    assert False
    a = 1
    assert False
    def b():
        assert False
        return 1
        assert False
'''
    expected = '''class A:
    a=1
    def b():
        return 1
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_from_class_empty():
    source = '''class A:
    assert False
'''
    expected = 'class A:0'

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_from_class_func_empty():
    source = '''class A:
    def b():
        assert False
'''
    expected = '''class A:
    def b(): 0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_asserts(source)
    compare_ast(expected_ast, actual_ast)
