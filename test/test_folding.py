import ast
import sys

import pytest

from python_minifier import minify
from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.constant_folding import FoldConstants, equal_value_and_type

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
        ('10-100', '-90'),
        ('1+1', '2'),
        ('2+2', '4'),
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


@pytest.mark.parametrize(
    ('source', 'expected'), [
        # Folding results in infinity, which can be represented as 1e999
        ('1e308 + 1e308', '1e999'),
        ('1e308 * 2', '1e999'),
    ]
)
def test_fold_infinity(source, expected):
    """
    Test that expressions resulting in infinity are folded to 1e999.

    Infinity can be represented as 1e999, which is shorter than
    the original expression.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        # Folding would result in NaN, which cannot be represented as a literal
        ('1e999 - 1e999', '1e999 - 1e999'),
        ('0.0 * 1e999', '0.0 * 1e999'),
    ]
)
def test_no_fold_nan(source, expected):
    """
    Test that expressions resulting in NaN are not folded.

    NaN is not a valid Python literal, so we cannot fold expressions
    that would produce it.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('100.0+100.0', '200.0'),
        ('1000.0+1000.0', '2000.0'),
    ]
)
def test_fold_float(source, expected):
    """
    Test that float expressions are folded when the result is shorter.
    """
    run_test(source, expected)


def test_equal_value_and_type():
    """
    Test the equal_value_and_type helper function.
    """

    # Same type and value
    assert equal_value_and_type(1, 1) is True
    assert equal_value_and_type(1.0, 1.0) is True
    assert equal_value_and_type(True, True) is True  # noqa: FBT003
    assert equal_value_and_type('hello', 'hello') is True

    # Different types
    assert equal_value_and_type(1, 1.0) is False
    assert equal_value_and_type(1, True) is False  # noqa: FBT003
    assert equal_value_and_type(True, 1) is False  # noqa: FBT003

    # Different values
    assert equal_value_and_type(1, 2) is False
    assert equal_value_and_type(1.0, 2.0) is False


def test_equal_value_and_type_nan():
    """
    Test the equal_value_and_type helper function with NaN values.
    """

    nan = float('nan')

    # NaN is not equal to itself in Python (nan != nan is True)
    # But if both are NaN, equal_value_and_type returns True via a == b
    # Since nan == nan is False, we need to check the actual behavior
    result = equal_value_and_type(nan, nan)
    # Python's nan == nan is False, so this should be False
    assert result is False

    # NaN compared to non-NaN should be False
    assert equal_value_and_type(nan, 1.0) is False
    assert equal_value_and_type(1.0, nan) is False


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('5 - 10', '-5'),
        ('0 - 100', '-100'),
        ('1.0 - 2.0', '-1.0'),
        ('0.0 - 100.0', '-100.0'),
    ]
)
def test_negative_results(source, expected):
    """
    Test BinOp expressions that produce negative results.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('5 * -2', '-10'),
        ('-5 * 2', '-10'),
        ('-5 + 10', '5'),
        ('-90 + 10', '-80'),
        ('10 - 20 + 5', '-5'),
        ('(5 - 10) * 2', '-10'),
        ('2 * (0 - 5)', '-10'),
        ('(1 - 10) + (2 - 20)', '-27'),
    ]
)
def test_negative_operands_folded(source, expected):
    """
    Test that expressions with negative operands are folded.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('-(-5)', '5'),
        ('--5', '5'),
        ('-(-100)', '100'),
        ('-(-(5 + 5))', '10'),
        ('~(~0)', '0'),
        ('~~5', '5'),
        ('~~100', '100'),
        ('+(+5)', '5'),
        ('+(-5)', '-5'),
    ]
)
def test_unary_folded(source, expected):
    """
    Test that unary operations on constant expressions are folded.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('not not True', 'True'),
        ('not not False', 'False'),
        ('not True', 'False'),
        ('not False', 'True'),
    ]
)
def test_unary_not_folded(source, expected):
    """
    Test that 'not' operations on constant expressions are folded.
    """
    if sys.version_info < (3, 4):
        pytest.skip('NameConstant not in python < 3.4')

    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('-5', '-5'),
        ('~5', '~5'),
    ]
)
def test_unary_simple_not_folded(source, expected):
    """
    Test that simple unary operations on literals are not folded
    when the result would not be shorter.
    """
    run_test(source, expected)


def test_unary_plus_folded():
    """
    Test that unary plus on a literal is folded to remove the plus.
    """
    run_test('+5', '5')


def test_not_false_in_conditional():
    """
    Test that 'not False' is folded to 'True' in a conditional.
    """
    if sys.version_info < (3, 4):
        pytest.skip('NameConstant not in python < 3.4')

    run_test('if not False:pass', 'if True:pass')


def test_not_not_true_in_assignment():
    """
    Test that 'not not True' is folded to 'True' in an assignment.
    """
    if sys.version_info < (3, 4):
        pytest.skip('NameConstant not in python < 3.4')

    run_test('x=not not True', 'x=True')


def test_bool_not_folded_before_34():
    """
    Test that boolean 'not' expressions are not folded in Python < 3.4.

    NameConstant was introduced in Python 3.4, so we cannot fold boolean
    constants in earlier versions.
    """
    if sys.version_info >= (3, 4):
        pytest.skip('Only applies to python < 3.4')

    run_test('if not False:pass', 'if not False:pass')
    run_test('x=not not True', 'x=not not True')


def test_constant_folding_enabled_by_default():
    """Verify constant folding is enabled by default."""
    source = 'x = 10 + 10'
    result = minify(source)
    assert '20' in result
    assert '10+10' not in result and '10 + 10' not in result  # noqa: PT018


def test_constant_folding_disabled():
    """Verify expressions are not folded when constant_folding=False."""
    source = 'x = 10 + 10'
    result = minify(source, constant_folding=False)
    assert '10+10' in result or '10 + 10' in result
    assert result.strip() != 'x=20'


def test_constant_folding_disabled_complex_expression():
    """Verify complex expressions are preserved when disabled."""
    source = 'SECONDS_IN_A_DAY = 60 * 60 * 24'
    result = minify(source, constant_folding=False)
    assert '60*60*24' in result or '60 * 60 * 24' in result


def test_constant_folding_enabled_complex_expression():
    """Verify complex expressions are folded when enabled."""
    source = 'SECONDS_IN_A_DAY = 60 * 60 * 24'
    result = minify(source, constant_folding=True)
    assert '86400' in result


@pytest.mark.parametrize(
    ('source', 'should_contain_when_disabled'), [
        ('x = 5 - 10', '5-10'),
        ('x = True | False', 'True|False'),
        ('x = 0xff ^ 0x0f', '255^15'),
    ]
)
def test_constant_folding_disabled_various_ops(source, should_contain_when_disabled):
    """Verify various operations are not folded when disabled."""
    if sys.version_info < (3, 4) and 'True' in source:
        pytest.skip('NameConstant not in python < 3.4')

    result = minify(source, constant_folding=False)
    assert should_contain_when_disabled in result.replace(' ', '')


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('1j + 2j', '3j'),
        ('3j * 2', '6j'),
        ('2 * 3j', '6j'),
        ('10j - 5j', '5j'),
    ]
)
def test_complex_folded(source, expected):
    """
    Test complex number operations that are folded.

    Complex operations are folded when the result is shorter than the original.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('1j - 2j', '1j-2j'),
        ('1j * 1j', '1j*1j'),
        ('0j + 5', '0j+5'),
        ('2j / 1j', '2j/1j'),
        ('1j ** 2', '1j**2'),
    ]
)
def test_complex_not_folded(source, expected):
    """
    Test complex number operations that are not folded.
    """
    if sys.version_info < (3, 0) and source == '1j - 2j':
        pytest.skip('Complex subtraction representation differs in Python 2')

    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        # These fold because the result is 0j or the folded form is shorter
        ('-3j + 3j', '0j'),
        ('1j + -1j', '0j'),
    ]
)
def test_negative_complex_in_binop_folded(source, expected):
    """
    Test that negative complex numbers (UnaryOp USub on complex) participate in BinOp folding.
    """
    if sys.version_info < (3, 0):
        pytest.skip('Complex number representation differs in Python 2')

    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('-3j + 1j', '-3j+1j'),
        ('-5j * 2', '-5j*2'),
        ('2 * -5j', '2*-5j'),
        ('-10j + 5j', '-10j+5j'),
    ]
)
def test_negative_complex_in_binop_not_folded(source, expected):
    """
    Test that some negative complex operations don't fold due to representation issues.

    When negating a pure imaginary number like -2j, Python represents -(-2j) as (-0+2j),
    which makes the folded form longer than the original expression.
    """
    if sys.version_info < (3, 0):
        pytest.skip('Complex number representation differs in Python 2')

    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('~0 + 1', '0'),
        ('~5 & 0xff', '250'),
        ('~0 | 5', '-1'),  # -1 in binary is all 1s, so -1 | x = -1
        ('1 + ~0', '0'),
        ('~1 + 2', '0'),
        ('~0xff & 0xff', '0'),
    ]
)
def test_invert_in_binop(source, expected):
    """
    Test that bitwise invert (UnaryOp Invert) participates in BinOp folding.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('~0', '~0'),
        ('~1', '~1'),
        ('~5', '~5'),
        ('~255', '~255'),
    ]
)
def test_invert_not_folded(source, expected):
    """
    Test that simple bitwise invert on literals is not folded when the result is not shorter.

    ~0 = -1, ~1 = -2, ~5 = -6, etc. These are the same length or longer.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('~~0', '0'),
        ('~~5', '5'),
        ('~~~0', '~0'),
        ('~~~~5', '5'),
    ]
)
def test_double_invert_folded(source, expected):
    """
    Test that double bitwise invert is folded.

    ~~x = x, so double invert should fold away.
    """
    run_test(source, expected)


@pytest.mark.parametrize(
    ('source', 'expected'), [
        # In Python, True == 1 and False == 0 for arithmetic
        ('-5 + True', '-4'),
        ('10 * False', '0'),
        ('True + True', '2'),
        ('~True', '-2'),  # ~1 = -2, shorter than ~True
        ('~False', '-1'),  # ~0 = -1, shorter than ~False
    ]
)
def test_mixed_numeric_bool_folded(source, expected):
    """
    Test folding of expressions mixing numeric and boolean operands.

    Python treats True as 1 and False as 0 in numeric contexts.
    """
    if sys.version_info < (3, 4):
        pytest.skip('NameConstant not in python < 3.4')

    run_test(source, expected)
