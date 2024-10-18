import ast
import sys

import pytest

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.constant_folding import FoldConstants


def fold_constants(source):
    module = ast.parse(source)
    add_parent(module)
    add_namespace(module)
    FoldConstants()(module)
    return module


def run_test(source, expected):
    try:
        expected_ast = ast.parse(expected)
    except SyntaxError:
        pytest.skip('Syntax not supported in this version of python')

    actual_ast = fold_constants(source)
    compare_ast(expected_ast, actual_ast)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('True | True', 'True'),
        ('True | False', 'True'),
        ('False | True', 'True'),
        ('False | False', 'False'),
        ('True & True', 'True'),
        ('True & False', 'False'),
        ('False & True', 'False'),
        ('False & False', 'False'),
        ('True ^ True', 'False'),
        ('True ^ False', 'True'),
        ('False ^ True', 'True'),
        ('False ^ False', 'False'),
        ('(True | True) | True', 'True'),
        ('(True | True) | False', 'True'),
        ('(True | False) | True', 'True'),
        ('(True | False) | False', 'True'),
        ('(False | True) | True', 'True'),
        ('(False | True) | False', 'True'),
        ('(False | False) | True', 'True'),
        ('(False | False) | False', 'False'),
        ('(True | True) & True', 'True'),
        ('(True | True) & False', 'False'),
        ('(True | False) & True', 'True'),
        ('(True | False) & False', 'False'),
        ('(False | True) & True', 'True'),
        ('(False | True) & False', 'False'),
        ('(False | False) & True', 'False'),
        ('(False | False) & False', 'False'),
        ('(True | True) ^ True', 'False'),
        ('(True | True) ^ False', 'True'),
        ('(True | False) ^ True', 'False'),
        ('(True | False) ^ False', 'True'),
        ('(False | True) ^ True', 'False'),
        ('(False | True) ^ False', 'True'),
        ('(False | False) ^ True', 'True'),
        ('(False | False) ^ False', 'False'),
        ('True | (True | True)', 'True'),
        ('True | (True | False)', 'True'),
        ('True | (False | True)', 'True'),
        ('True | (False | False)', 'True'),
        ('False | (True | True)', 'True'),
        ('False | (True | False)', 'True'),
        ('False | (False | True)', 'True'),
        ('False | (False | False)', 'False'),
    ]
)
def test_bool(source, expected):
    """
    Test BinOp with bool operands

    This is mainly testing we fold the constants correctly
    """

    if sys.version_info < (3, 4):
        pytest.skip('NameConstant not in python < 3.4')

    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('10 + 10', '20'),
        ('10 + 0', '10'),
        ('0 + 10', '10'),
        ('10 + 10 + 5', '25'),
        ('10 - 5 + 5', '10'),
        ('10 * 10', '100'),
        ('10 * 10 * 10', '1000'),
        ('(10 * 10) // 10', '10'),
        ('(2 * 10) // (2+2)', '5'),
        ('8>>2', '2'),
        ('8<<2', '32'),
        ('0xff^0x0f', '0xf0'),
        ('0xf0&0xff', '0xf0'),
        ('0xf0|0x0f', '0xff'),
        ('10%2', '0'),
        ('10%3', '1'),
        ('10-100', '-90')
    ]
)
def test_int(source, expected):
    """
    Test BinOp with integer operands we can fold
    """

    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('10/10', '10/10'),
        ('5+5/10', '5+5/10'),
        ('2*5/10', '10/10'),
        ('2/5*10', '2/5*10'),
        ('2**5', '2**5'),
        ('5@6', '5@6'),
    ]
)
def test_int_not_eval(source, expected):
    """
    Test BinOp with operations we don't want to fold
    """

    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('"Hello" + "World"', '"Hello" + "World"'),
        ('"Hello" * 5', '"Hello" * 5'),
        ('b"Hello" + b"World"', 'b"Hello" + b"World"'),
        ('b"Hello" * 5', 'b"Hello" * 5'),
    ]
)
def test_not_eval(source, expected):
    """
    Test BinOps we don't want to fold
    """

    run_test(source, expected)
