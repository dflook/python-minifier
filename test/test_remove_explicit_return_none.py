import ast
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast
from python_minifier.transforms.implicit_return_none import implicit_return_none


def remove_return_none(source):
    module = ast.parse(source, 'remove_return_none')

    return implicit_return_none(module)

def test_remove_return_none():
    source = 'def a():return None'
    expected = 'def a():return'

    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)

    assert unparse(actual_ast) == expected

def test_implicit_return_none():
    source = 'def a():return'
    expected = source
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected

def test_return_value_unchanged():
    source = 'def a():return 0'
    expected = source
    expected_ast = ast.parse(expected)
    actual_ast = remove_return_none(source)
    compare_ast(expected_ast, actual_ast)
    assert unparse(actual_ast) == expected

