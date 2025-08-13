# -*- coding: utf-8 -*-
import tempfile
import os
import sys
import codecs

from subprocess_compat import run_subprocess, safe_decode


def test_cli_output_flag_with_unicode():
    """
    Tests that the CLI tool can write Unicode characters to files using --output flag.
    """
    # Minimal source with all problematic Unicode characters from reported issues
    source_code = u'print(u"❌ ✓ 🐍 Привет © ∀")'

    source_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False)
    source_file.write(source_code.encode('utf-8'))
    source_file.close()

    output_path = source_file.name + '.min.py'

    try:
        # Run pyminify CLI with --output flag
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier',
            source_file.name, '--output', output_path
        ], timeout=30)

        assert result.returncode == 0, "CLI failed with encoding error: {}".format(safe_decode(result.stderr))

        # Verify the output file was created and contains Unicode characters
        if sys.version_info[0] >= 3:
            with open(output_path, 'r', encoding='utf-8') as f:
                minified_content = f.read()
        else:
            with codecs.open(output_path, 'r', encoding='utf-8') as f:
                minified_content = f.read()

        # Verify problematic Unicode characters are preserved
        if hasattr(sys, 'pypy_version_info') and sys.version_info[0] >= 3:
            # PyPy3: Unicode characters may be escaped as \\u escapes
            assert "\\u274c" in minified_content
            assert "✓" in minified_content
            assert "\\U0001f40d" in minified_content
            assert "Привет" in minified_content
            assert "©" in minified_content
            assert "∀" in minified_content
        elif hasattr(sys, 'pypy_version_info') and sys.version_info[0] < 3:
            # PyPy2: Unicode characters appear as UTF-8 byte sequences
            assert "\\xe2\\x9d\\x8c" in minified_content  # ❌
            assert "\\xe2\\x9c\\x93" in minified_content  # ✓
            assert "\\xf0\\x9f\\x90\\x8d" in minified_content  # 🐍
        elif sys.version_info[0] >= 3:
            # CPython 3: Unicode characters should appear literally
            assert "❌" in minified_content
            assert "✓" in minified_content
            assert "🐍" in minified_content
            assert "Привет" in minified_content
            assert "©" in minified_content
            assert "∀" in minified_content
        else:
            # Python 2.7: Check for escaped sequences or use Unicode literals
            assert u"\\xe2\\x9d\\x8c" in minified_content
            assert u"\\xe2\\x9c\\x93" in minified_content
            assert u"\\xf0\\x9f\\x90\\x8d" in minified_content

    finally:
        # Cleanup
        if os.path.exists(source_file.name):
            os.unlink(source_file.name)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_cli_in_place_with_unicode():
    """
    Tests that the CLI tool can write Unicode characters to files using --in-place flag.
    """
    source_code = u'print(u"❌ ✓ 🐍 Привет © ∀")'

    temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False)
    temp_file.write(source_code.encode('utf-8'))
    temp_file.close()

    try:
        # Run pyminify with --in-place flag
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier',
            temp_file.name, '--in-place'
        ], timeout=30)

        assert result.returncode == 0, "CLI failed with encoding error: {}".format(safe_decode(result.stderr))

        if sys.version_info[0] >= 3:
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            with codecs.open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

        if hasattr(sys, 'pypy_version_info') and sys.version_info[0] >= 3:
            # PyPy3: Unicode characters may be escaped as \\u escapes
            assert "✓" in content
            assert "\\u274c" in content  # ❌
            assert "\\U0001f40d" in content  # 🐍
            assert "Привет" in content
            assert "©" in content
            assert "∀" in content
        elif hasattr(sys, 'pypy_version_info') and sys.version_info[0] < 3:
            # PyPy2: Unicode characters appear as UTF-8 byte sequences
            assert "\\xe2\\x9c\\x93" in content  # ✓
            assert "\\xe2\\x9d\\x8c" in content  # ❌
            assert "\\xf0\\x9f\\x90\\x8d" in content  # 🐍
        elif sys.version_info[0] >= 3:
            # CPython 3: Unicode characters should appear literally
            assert "✓" in content
            assert "❌" in content
            assert "🐍" in content
            assert "Привет" in content
            assert "©" in content
            assert "∀" in content
        else:
            # Python 2.7: Unicode characters appear as escaped sequences
            assert "\\xe2\\x9d\\x8c" in content  # ❌
            assert "\\xe2\\x9c\\x93" in content  # ✓
            assert "\\xf0\\x9f\\x90\\x8d" in content  # 🐍

    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


def test_cli_stdout_with_unicode():
    """
    Tests that the CLI tool can write Unicode characters to stdout.
    """
    source_code = u'print(u"❌ ✓ 🐍 Привет © ∀")'

    temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False)
    temp_file.write(source_code.encode('utf-8'))
    temp_file.close()

    try:
        # Run without --output or --in-place (should output to stdout)
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier', temp_file.name
        ], timeout=30)

        assert result.returncode == 0, "Stdout output failed: {}".format(safe_decode(result.stderr))

        stdout_text = safe_decode(result.stdout)

        if hasattr(sys, 'pypy_version_info') and sys.version_info[0] >= 3:
            # PyPy3: Unicode characters may be escaped as \\u escapes
            assert "\\u274c" in stdout_text  # ❌
            assert "✓" in stdout_text   # ✓
            assert "\\U0001f40d" in stdout_text  # 🐍
            assert "Привет" in stdout_text  # Привет
            assert "©" in stdout_text   # ©
            assert "∀" in stdout_text   # ∀
        elif sys.version_info[0] >= 3:
            # CPython 3: Unicode characters should appear literally
            assert "❌" in stdout_text
            assert "✓" in stdout_text
            assert "🐍" in stdout_text
            assert "Привет" in stdout_text
            assert "©" in stdout_text
            assert "∀" in stdout_text
        else:
            # Python 2.7: Unicode characters appear as escaped sequences
            assert "\\xe2\\x9d\\x8c" in stdout_text  # ❌
            assert "\\xe2\\x9c\\x93" in stdout_text  # ✓
            assert "\\xf0\\x9f\\x90\\x8d" in stdout_text  # 🐍

    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
