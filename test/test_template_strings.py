import ast
import sys

import pytest

from python_minifier import unparse
from python_minifier.ast_compare import compare_ast


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
@pytest.mark.parametrize(
    'statement', [
        't"hello"',
        't"Hello {name}"',
        't"Hello {name!r}"',
        't"Hello {name!s}"',
        't"Hello {name!a}"',
        't"Value: {value:.2f}"',
        't"{1}"',
        't"{1=}"',
        't"{1=!r:.4}"',
        't"{1=:.4}"',
        't"{1=!s:.4}"',
        't"{1=!a}"',
    ]
)
def test_tstring_basic(statement):
    """Test basic t-string parsing and unparsing"""
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
@pytest.mark.parametrize(
    'statement', [
        't"Hello {name} and {other}"',
        't"User {action}: {amount:.2f} {item}"',
        't"{value:.{precision}f}"',
        't"Complex {a} and {b!r} with {c:.3f}"',
    ]
)
def test_tstring_multiple_interpolations(statement):
    """Test t-strings with multiple interpolations"""
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
@pytest.mark.parametrize(
    'statement', [
        't"nested {t"inner {x}"}"',
        't"outer {t"middle {t"inner {y}"}"} end"',
        't"complex {t"nested {value:.2f}"} result"',
        't"{t"prefix {name}"} suffix"',
    ]
)
def test_tstring_nesting(statement):
    """Test nested t-strings (should work with PEP 701 benefits)"""
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_quote_variations():
    """Test different quote styles for t-strings - just ensure they parse and unparse correctly"""
    statements = [
        "t'single quotes {name}'",
        't"""triple double quotes {name}"""',
        "t'''triple single quotes {name}'''",
        't"mixed {name} with \\"escaped\\" quotes"',
        "t'mixed {name} with \\'escaped\\' quotes'",
    ]
    
    for statement in statements:
        # Just test that it parses and round-trips correctly, don't care about exact quote style
        parsed = ast.parse(statement)
        unparsed = unparse(parsed)
        reparsed = ast.parse(unparsed)
        compare_ast(parsed, reparsed)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_multiline():
    """Test multiline t-strings"""
    statement = '''t"""
Multiline template
with {name} interpolation
and {value:.2f} formatting
"""'''
    expected = 't"\\nMultiline template\\nwith {name} interpolation\\nand {value:.2f} formatting\\n"'
    assert unparse(ast.parse(statement)) == expected


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_with_complex_expressions():
    """Test t-strings with complex expressions in interpolations"""
    test_cases = [
        ('t"Result: {func(a, b, c)}"', 't"Result: {func(a,b,c)}"'),
        ('t"List: {[x for x in items]}"', 't"List: {[x for x in items]}"'),
        ('t"Dict: {key: value for key, value in pairs}"', 't"Dict: {key: value for key, value in pairs}"'),
        ('t"Set: {{item for item in collection}}"', 't"Set: {{item for item in collection}}"'),
        ('t"Lambda: {(lambda x: x * 2)(value)}"', 't"Lambda: {((lambda x:x*2))(value)}"'),
        ('t"Attribute: {obj.attr.method()}"', 't"Attribute: {obj.attr.method()}"'),
        ('t"Subscription: {data[key][0]}"', 't"Subscription: {data[key][0]}"'),
        ('t"Ternary: {x if condition else y}"', 't"Ternary: {x if condition else y}"'),
    ]
    
    for input_statement, expected_output in test_cases:
        assert unparse(ast.parse(input_statement)) == expected_output


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_with_binary_operations():
    """Test t-strings with binary operations in interpolations"""
    test_cases = [
        ('t"Sum: {a + b}"', 't"Sum: {a+b}"'),
        ('t"Product: {x * y}"', 't"Product: {x*y}"'),
        ('t"Division: {total / count}"', 't"Division: {total/count}"'),
        ('t"Complex: {(a + b) * (c - d)}"', 't"Complex: {(a+b)*(c-d)}"'),
        ('t"String concat: {first + last}"', 't"String concat: {first+last}"'),
        ('t"Comparison: {x > y}"', 't"Comparison: {x>y}"'),
        ('t"Boolean: {a and b}"', 't"Boolean: {a and b}"'),
        ('t"Bitwise: {x | y}"', 't"Bitwise: {x|y}"'),
    ]
    
    for input_statement, expected_output in test_cases:
        assert unparse(ast.parse(input_statement)) == expected_output


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_empty():
    """Test empty t-string"""
    statement = 't""'
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_only_interpolation():
    """Test t-string with only interpolation, no literal parts"""
    statement = 't"{value}"'
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_special_characters():
    """Test t-strings with special characters that need escaping"""
    statements = [
        't"Braces: {{literal}} and {variable}"',
        't"Newline: \\n and {value}"',
        't"Tab: \\t and {value}"',
        't"Quote: \\" and {value}"',
        "t'Quote: \\' and {value}'",
        't"Backslash: \\\\ and {value}"',
    ]
    
    for statement in statements:
        # Test that it parses and round-trips correctly
        parsed = ast.parse(statement)
        unparsed = unparse(parsed)
        reparsed = ast.parse(unparsed)
        compare_ast(parsed, reparsed)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_ast_structure():
    """Test that t-string AST structure is correctly preserved"""
    source = 't"Hello {name} world {value:.2f}!"'
    expected_ast = ast.parse(source)  # Parse as module, not expression
    actual_ast = ast.parse(unparse(expected_ast))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_vs_fstring_syntax():
    """Test that t-strings and f-strings have similar but distinct syntax"""
    # These should both parse successfully but produce different ASTs
    tstring = 't"Hello {name}"'
    fstring = 'f"Hello {name}"'
    
    t_ast = ast.parse(tstring)
    f_ast = ast.parse(fstring)
    
    # Should be different node types in the expression
    assert type(t_ast.body[0].value).__name__ == 'TemplateStr'
    assert type(f_ast.body[0].value).__name__ == 'JoinedStr'
    
    # But should unparse correctly
    assert unparse(t_ast) == tstring
    assert unparse(f_ast) == fstring


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_raw_template_strings():
    """Test raw template strings (rt prefix) - they parse but unparser loses the raw prefix"""
    if sys.version_info >= (3, 14):  # Raw t-strings are supported in Python 3.14
        # Test that raw t-strings parse correctly
        raw_statements = [
            'rt"raw template {name}"',
            'rt"backslash \\\\ preserved {name}"',
        ]
        
        for statement in raw_statements:
            # Raw t-strings should parse successfully
            ast.parse(statement)
            
        # Test that raw behavior is preserved in the AST even if prefix is lost
        raw_backslash = 'rt"backslash \\\\n and {name}"'
        regular_backslash = 't"backslash \\n and {name}"'  # Only two backslashes for regular
        
        raw_ast = ast.parse(raw_backslash)
        regular_ast = ast.parse(regular_backslash)
        
        # The AST should show different string content
        raw_content = raw_ast.body[0].value.values[0].value
        regular_content = regular_ast.body[0].value.values[0].value
        
        # Raw should have literal backslash-n, regular should have actual newline
        assert '\\\\n' in raw_content  # literal backslash-n (two chars: \ and n)
        assert '\n' in regular_content  # actual newline character
        assert raw_content != regular_content


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_debug_specifier_limitations():
    """Test debug specifier limitations (same as f-strings)"""
    # Debug specifiers work when at the start of the string
    assert unparse(ast.parse('t"{name=}"')) == 't"{name=}"'
    assert unparse(ast.parse('t"{value=:.2f}"')) == 't"{value=:.2f}"'
    
    # But are lost when there's a preceding literal (same limitation as f-strings)
    assert unparse(ast.parse('t"Hello {name=}"')) == 't"Hello name={name!r}"'
    assert unparse(ast.parse('t"Hello {name=!s}"')) == 't"Hello name={name!s}"'
    assert unparse(ast.parse('t"Hello {name=:.2f}"')) == 't"Hello name={name:.2f}"'
    
    # This matches f-string behavior exactly
    assert unparse(ast.parse('f"Hello {name=}"')) == 'f"Hello name={name!r}"'


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template strings require Python 3.14+")
def test_tstring_error_conditions():
    """Test that our implementation handles edge cases properly"""
    # Test round-trip parsing for complex cases
    complex_cases = [
        't"Deep {t"nesting {t"level {x}"}"} works"',
        't"Format {value:{width}.{precision}f} complex"',
        't"Mixed {a!r} and {b=:.2f} specifiers"',
    ]
    
    for case in complex_cases:
        try:
            # Parse as module, not expression
            expected_ast = ast.parse(case)
            unparsed = unparse(expected_ast)
            actual_ast = ast.parse(unparsed)
            compare_ast(expected_ast, actual_ast)
        except Exception as e:
            pytest.fail("Failed to handle complex case {}: {}".format(case, e))