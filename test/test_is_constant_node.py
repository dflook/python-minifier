import sys

import pytest

import ast

from python_minifier.util import is_constant_node


@pytest.mark.filterwarnings("ignore:ast.Str is deprecated:DeprecationWarning")
@pytest.mark.filterwarnings("ignore:ast.Bytes is deprecated:DeprecationWarning") 
@pytest.mark.filterwarnings("ignore:ast.Num is deprecated:DeprecationWarning")
@pytest.mark.filterwarnings("ignore:ast.NameConstant is deprecated:DeprecationWarning")
@pytest.mark.filterwarnings("ignore:ast.Ellipsis is deprecated:DeprecationWarning")
def test_type_nodes():
    if sys.version_info >= (3, 14):
        pytest.skip('Deprecated AST types removed in Python 3.14')
    assert is_constant_node(ast.Str('a'), ast.Str)

    if hasattr(ast, 'Bytes'):
        assert is_constant_node(ast.Bytes(b'a'), ast.Bytes)

    assert is_constant_node(ast.Num(1), ast.Num)
    assert is_constant_node(ast.Num(0), ast.Num)

    if hasattr(ast, 'NameConstant'):
        assert is_constant_node(ast.NameConstant(True), ast.NameConstant)
        assert is_constant_node(ast.NameConstant(False), ast.NameConstant)
        assert is_constant_node(ast.NameConstant(None), ast.NameConstant)
    else:
        assert is_constant_node(ast.Name(id='True', ctx=ast.Load()), ast.Name)
        assert is_constant_node(ast.Name(id='False', ctx=ast.Load()), ast.Name)
        assert is_constant_node(ast.Name(id='None', ctx=ast.Load()), ast.Name)

    assert is_constant_node(ast.Ellipsis(), ast.Ellipsis)


@pytest.mark.filterwarnings("ignore:ast.Str is deprecated:DeprecationWarning")
@pytest.mark.filterwarnings("ignore:ast.Bytes is deprecated:DeprecationWarning") 
@pytest.mark.filterwarnings("ignore:ast.Num is deprecated:DeprecationWarning")
@pytest.mark.filterwarnings("ignore:ast.NameConstant is deprecated:DeprecationWarning")
@pytest.mark.filterwarnings("ignore:ast.Ellipsis is deprecated:DeprecationWarning")
def test_constant_nodes():
    # only test on python 3.8+
    if sys.version_info < (3, 8):
        pytest.skip('Constant not available')
    if sys.version_info >= (3, 14):
        pytest.skip('Deprecated AST types removed in Python 3.14')

    assert is_constant_node(ast.Constant('a'), ast.Str)
    assert is_constant_node(ast.Constant(b'a'), ast.Bytes)
    assert is_constant_node(ast.Constant(1), ast.Num)
    assert is_constant_node(ast.Constant(0), ast.Num)
    assert is_constant_node(ast.Constant(True), ast.NameConstant)
    assert is_constant_node(ast.Constant(False), ast.NameConstant)
    assert is_constant_node(ast.Constant(None), ast.NameConstant)
    assert is_constant_node(ast.Constant(ast.literal_eval('...')), ast.Ellipsis)


def test_ast_compat_types_python314():
    """Test that ast_compat provides the removed AST types in Python 3.14+"""
    if sys.version_info < (3, 14):
        pytest.skip('ast_compat types test only for Python 3.14+')
    
    import python_minifier.ast_compat as ast_compat
    
    # Test that ast_compat provides the removed types
    assert is_constant_node(ast_compat.Str('a'), ast_compat.Str)
    assert is_constant_node(ast_compat.Bytes(b'a'), ast_compat.Bytes)
    assert is_constant_node(ast_compat.Num(1), ast_compat.Num)
    assert is_constant_node(ast_compat.Num(0), ast_compat.Num)
    assert is_constant_node(ast_compat.NameConstant(True), ast_compat.NameConstant)
    assert is_constant_node(ast_compat.NameConstant(False), ast_compat.NameConstant)
    assert is_constant_node(ast_compat.NameConstant(None), ast_compat.NameConstant)
    assert is_constant_node(ast_compat.Ellipsis(), ast_compat.Ellipsis)


def test_ast_compat_constant_nodes_python314():
    """Test that ast_compat works with Constant nodes in Python 3.14+"""
    if sys.version_info < (3, 14):
        pytest.skip('ast_compat constant test only for Python 3.14+')
    
    import python_minifier.ast_compat as ast_compat
    
    # Test that Constant nodes work with ast_compat types
    assert is_constant_node(ast.Constant('a'), ast_compat.Str)
    assert is_constant_node(ast.Constant(b'a'), ast_compat.Bytes)
    assert is_constant_node(ast.Constant(1), ast_compat.Num)
    assert is_constant_node(ast.Constant(0), ast_compat.Num)
    assert is_constant_node(ast.Constant(True), ast_compat.NameConstant)
    assert is_constant_node(ast.Constant(False), ast_compat.NameConstant)
    assert is_constant_node(ast.Constant(None), ast_compat.NameConstant)
    assert is_constant_node(ast.Constant(ast.literal_eval('...')), ast_compat.Ellipsis)
