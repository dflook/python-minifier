"""
Test for raw f-string with backslash escape sequences.

This test covers the fix for issue where raw f-strings containing backslash
escape sequences in format specs would fail with "Unable to create representation 
for f-string" error.
"""

import ast
import sys

import pytest

from python_minifier import unparse
from python_minifier.ast_compare import compare_ast


def test_raw_fstring_backslash_format_spec():
    """Test that raw f-strings with backslash escapes in format specs can be unparsed correctly."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    # This is the minimal case that was failing before the fix
    source = 'rf"{x:\\xFF}"'
    
    # This should round-trip correctly without "Unable to create representation for f-string"
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_raw_fstring_backslash_outer_str():
    """Test that raw f-strings with backslashes in the outer string parts can be unparsed correctly."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    # Test backslashes in the literal parts of raw f-strings
    source = r'rf"\\n{x}\\t"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_raw_fstring_mixed_backslashes():
    """Test raw f-strings with backslashes in both literal parts and format specs."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    # Test combination of backslashes in literal parts and format specs
    source = r'rf"\\n{x:\\xFF}\\t"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_nested_fstring_backslashes():
    """Test nested f-strings with backslashes (Python 3.12+ only)."""
    
    if sys.version_info < (3, 12):
        pytest.skip('Nested f-strings not supported in Python < 3.12')
    
    # Test nested f-strings with backslashes in inner string parts
    source = r'f"{f"\\n{x}\\t"}"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_nested_raw_fstring_backslashes():
    """Test nested raw f-strings with backslashes (Python 3.12+ only)."""
    
    if sys.version_info < (3, 12):
        pytest.skip('Nested f-strings not supported in Python < 3.12')
    
    # Test nested raw f-strings with backslashes
    source = r'f"{rf"\\xFF{y}\\n"}"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_nested_fstring_format_spec_backslashes():
    """Test nested f-strings with backslashes in format specs (Python 3.12+ only)."""
    
    if sys.version_info < (3, 12):
        pytest.skip('Nested f-strings not supported in Python < 3.12')
    
    # Test nested f-strings with backslashes in format specifications
    source = r'f"{f"{x:\\xFF}"}"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_raw_fstring_literal_single_backslash():
    """Test raw f-string with single backslash in literal part only."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    source = r'rf"\n"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_raw_fstring_literal_double_backslash():
    """Test raw f-string with double backslash in literal part only."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    source = r'rf"\\n"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_raw_fstring_formatspec_single_backslash():
    """Test raw f-string with single backslash in format spec only."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    source = r'rf"{x:\xFF}"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_raw_fstring_formatspec_double_backslash():
    """Test raw f-string with double backslash in format spec only."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    source = r'rf"{x:\\xFF}"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))


def test_raw_fstring_mixed_single_backslashes():
    """Test raw f-string with single backslashes in both literal and format spec parts."""
    
    if sys.version_info < (3, 6):
        pytest.skip('F-strings not supported in Python < 3.6')
    
    source = r'rf"\n{x:\xFF}\t"'
    
    expected_ast = ast.parse(source)
    actual_code = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_code))