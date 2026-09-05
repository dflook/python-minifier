"""Tests for the quote style chosen for string literals."""

from python_minifier import minify


def test_no_quotes_uses_single_quotes():
    assert minify('print("")') == "print('')"


def test_single_quote_in_string_uses_double_quotes():
    assert minify('print(\'\\\'\')') == 'print("\'")'


def test_tie_prefers_single_quotes():
    assert minify('print("\'\\"")') == 'print(\'\\\'"\')'


def test_more_single_quotes_than_double_uses_double_quotes():
    # A string with more single quotes than double quotes must not be
    # rendered with every single quote escaped, which made the output
    # longer than the input.
    assert minify('print("\'\\"\'")') == 'print("\'\\"\'")'
