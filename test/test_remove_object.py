import ast
import pytest
import sys

from python_minifier.transforms.remove_object_base import RemoveObject
from python_minifier.ast_compare import compare_ast


def test_remove_object_py3():
    if sys.version_info < (3, 0):
        pytest.skip('This test is python3 only')

    source = '''
class Test(object):
    pass
'''
    expected = '''
class Test:
    pass
'''

    expected_ast = ast.parse(expected)
    actual_ast = RemoveObject()(ast.parse(source))
    compare_ast(expected_ast, actual_ast)

    source = '''
class Test(another_base, object, third_base):
    pass
'''
    expected = '''
class Test(another_base, third_base):
    pass
'''

    expected_ast = ast.parse(expected)
    actual_ast = RemoveObject()(ast.parse(source))
    compare_ast(expected_ast, actual_ast)

    expected_ast = ast.parse(expected)
    actual_ast = RemoveObject()(ast.parse(source))
    compare_ast(expected_ast, actual_ast)

    source = '''
class Test(other_base):
    pass
'''
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = RemoveObject()(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


def test_no_remove_object_py2():
    if sys.version_info >= (3, 0):
        pytest.skip('This test is python2 only')

    source = '''
class Test(object):
    pass
'''
    expected = '''
class Test(object):
    pass
'''

    expected_ast = ast.parse(expected)
    actual_ast = RemoveObject()(ast.parse(source))
    compare_ast(expected_ast, actual_ast)

