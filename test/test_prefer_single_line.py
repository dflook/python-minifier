"""Tests for the prefer_single_line option."""
import ast
import sys
import os
import tempfile

from python_minifier import minify, unparse
from python_minifier.ast_annotation import add_parent
from python_minifier.rename import add_namespace

from subprocess_compat import run_subprocess, safe_decode


# minify() tests

def test_minify_default_uses_newlines():
    """Default behavior uses newlines between module-level statements."""
    source = '''
a = 1
b = 2
c = 3
'''
    expected = 'a=1\nb=2\nc=3'
    assert minify(source) == expected


def test_minify_prefer_single_line_false_uses_newlines():
    """prefer_single_line=False uses newlines between module-level statements."""
    source = '''
a = 1
b = 2
c = 3
'''
    expected = 'a=1\nb=2\nc=3'
    assert minify(source, prefer_single_line=False) == expected


def test_minify_prefer_single_line_true_uses_semicolons():
    """prefer_single_line=True uses semicolons between module-level statements."""
    source = '''
a = 1
b = 2
c = 3
'''
    expected = 'a=1;b=2;c=3'
    assert minify(source, prefer_single_line=True) == expected


def test_minify_single_statement_no_trailing_separator():
    """Single statement has no trailing separator regardless of option."""
    source = 'a = 1'
    expected = 'a=1'
    assert minify(source, prefer_single_line=False) == expected
    assert minify(source, prefer_single_line=True) == expected


def test_minify_empty_module():
    """Empty module produces empty output."""
    source = ''
    expected = ''
    assert minify(source, prefer_single_line=False) == expected
    assert minify(source, prefer_single_line=True) == expected


def test_minify_function_body_uses_semicolons():
    """Function body statements use semicolons regardless of option."""
    source = '''
def f():
    a = 1
    b = 2
    return a + b
'''
    # Both produce identical output since the option only affects module level
    expected = 'def f():A=1;B=2;return A+B'
    assert minify(source, prefer_single_line=False) == expected
    assert minify(source, prefer_single_line=True) == expected


def test_minify_class_body_uses_semicolons():
    """Class body statements use semicolons regardless of option."""
    source = '''
class C:
    a = 1
    b = 2
'''
    # Both produce identical output since the option only affects module level
    expected = 'class C:a=1;b=2'
    assert minify(source, prefer_single_line=False) == expected
    assert minify(source, prefer_single_line=True) == expected


def test_minify_mixed_module_and_function():
    """Compound statements like def require newlines regardless of option."""
    source = '''
x = 1
def f():
    a = 1
    b = 2
y = 2
'''
    # Both outputs are identical because compound statements require newlines
    expected = 'x=1\ndef f():A=1;B=2\ny=2'
    assert minify(source, prefer_single_line=False) == expected
    assert minify(source, prefer_single_line=True) == expected


def test_minify_imports():
    """Import statements respect prefer_single_line option."""
    source = '''
import os
import sys
a = 1
'''
    # Imports are combined, module-level separator differs
    expected_newlines = 'import os,sys\na=1'
    expected_semicolons = 'import os,sys;a=1'
    assert minify(source, prefer_single_line=False) == expected_newlines
    assert minify(source, prefer_single_line=True) == expected_semicolons


# unparse() tests

def _prepare_module(source):
    """Parse and annotate a module for unparsing."""
    module = ast.parse(source)
    add_parent(module)
    add_namespace(module)
    return module


def test_unparse_default_uses_newlines():
    """unparse() default uses newlines."""
    source = 'a=1\nb=2'
    expected = 'a=1\nb=2'
    module = _prepare_module(source)
    assert unparse(module) == expected


def test_unparse_prefer_single_line_false():
    """unparse() with prefer_single_line=False uses newlines."""
    source = 'a=1\nb=2'
    expected = 'a=1\nb=2'
    module = _prepare_module(source)
    assert unparse(module, prefer_single_line=False) == expected


def test_unparse_prefer_single_line_true():
    """unparse() with prefer_single_line=True uses semicolons."""
    source = 'a=1\nb=2'
    expected = 'a=1;b=2'
    module = _prepare_module(source)
    assert unparse(module, prefer_single_line=True) == expected


# CLI tests

def _normalize_newlines(text):
    """Normalize line endings for cross-platform comparison."""
    return text.replace('\r\n', '\n')


def test_cli_default_uses_newlines():
    """CLI without --prefer-single-line uses newlines."""
    code = 'a = 1\nb = 2\nc = 3'
    expected = 'a=1\nb=2\nc=3'

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier', temp_file
        ], timeout=30)

        assert result.returncode == 0
        stdout_text = _normalize_newlines(safe_decode(result.stdout))
        assert stdout_text == expected
    finally:
        os.unlink(temp_file)


def test_cli_prefer_single_line_flag():
    """CLI with --prefer-single-line uses semicolons."""
    code = 'a = 1\nb = 2\nc = 3'
    expected = 'a=1;b=2;c=3'

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier',
            '--prefer-single-line', temp_file
        ], timeout=30)

        assert result.returncode == 0
        stdout_text = safe_decode(result.stdout)
        assert stdout_text == expected
    finally:
        os.unlink(temp_file)


def test_cli_stdin_prefer_single_line():
    """CLI --prefer-single-line works with stdin."""
    code = 'a = 1\nb = 2\nc = 3'
    expected = 'a=1;b=2;c=3'

    result = run_subprocess([
        sys.executable, '-m', 'python_minifier',
        '--prefer-single-line', '-'
    ], input_data=code, timeout=30)

    assert result.returncode == 0
    stdout_text = safe_decode(result.stdout)
    assert stdout_text == expected
