import sys

import pytest

import python_minifier.ast_compat as ast
from python_minifier.util import is_ast_node

def test_type_nodes():
    assert is_ast_node(ast.Str('a'), ast.Str)

    if hasattr(ast, 'Bytes'):
        assert is_ast_node(ast.Bytes(b'a'), ast.Bytes)

    assert is_ast_node(ast.Num(1), ast.Num)
    assert is_ast_node(ast.Num(0), ast.Num)

    if hasattr(ast, 'NameConstant'):
        assert is_ast_node(ast.NameConstant(True), ast.NameConstant)
        assert is_ast_node(ast.NameConstant(False), ast.NameConstant)
        assert is_ast_node(ast.NameConstant(None), ast.NameConstant)
    else:
        assert is_ast_node(ast.Name(id='True', ctx=ast.Load()), ast.Name)
        assert is_ast_node(ast.Name(id='False', ctx=ast.Load()), ast.Name)
        assert is_ast_node(ast.Name(id='None', ctx=ast.Load()), ast.Name)

    assert is_ast_node(ast.Ellipsis(), ast.Ellipsis)

def test_constant_nodes():
    # only test on python 3.8+
    if sys.version_info < (3, 8):
        pytest.skip('Constant not available')

    assert is_ast_node(ast.Constant('a'), ast.Str)
    assert is_ast_node(ast.Constant(b'a'), ast.Bytes)
    assert is_ast_node(ast.Constant(1), ast.Num)
    assert is_ast_node(ast.Constant(0), ast.Num)
    assert is_ast_node(ast.Constant(True), ast.NameConstant)
    assert is_ast_node(ast.Constant(False), ast.NameConstant)
    assert is_ast_node(ast.Constant(None), ast.NameConstant)
    assert is_ast_node(ast.Constant(ast.literal_eval('...')), ast.Ellipsis)
