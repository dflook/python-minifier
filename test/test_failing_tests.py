"""
Tests that are expected to fail currently
"""
import ast

import pytest

from python_minifier import UnstableMinification, minify, unparse


@pytest.mark.xfail(reason="Known unstable minification")
def test_unstable_minification():
    """
    Known unstable minifications that need to be fixed
    """

    with pytest.raises(UnstableMinification):
        minify('with (x := await a, y := await b): pass')


@pytest.mark.xfail(reason="Known un-optimal minification")
def test_name_following_literal_number():
    """
    Name following literal number without a space

    This is a syntax warning in recent versions of Python,
    perhaps we should consider making this an optional minification
    """

    source = 'True if 0in x else False'
    assert source == unparse(ast.parse(source))


@pytest.mark.xfail(reason="Known un-optimal minification")
def test_generator_parentheses():
    """
    Generator expression parentheses

    Generator expressions are not always required to be parenthesized,
    but we currently always parenthesize them
    """

    source = 'sum(A for A in A)'
    assert source == unparse(ast.parse(source))


@pytest.mark.xfail(reason="Known un-optimal minification")
def test_generator_in_arglist():
    """
    Expanding a generator expression in an function call argument list
    """

    source = 'A(*[B for b in a])'
    assert source == unparse(ast.parse(source))


@pytest.mark.xfail(reason="Known un-optimal minification")
def test_tuple_in_for_target():
    """
    A tuple in a for target has unnecessary parentheses
    """

    source = 'for A,B in C:pass'
    assert source == unparse(ast.parse(source))


@pytest.mark.xfail(reason="Known un-optimal minification")
def test_string_literal_style():
    """
    String literals don't choose the smallest quote style
    """

    source = '''my_string="""This


is


my


multi-line

 
string


"""
'''
    assert source == unparse(ast.parse(source))
