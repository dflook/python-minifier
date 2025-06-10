# -*- coding: utf-8 -*-
import pytest
import tempfile
import os
import subprocess
import sys
import locale
import codecs

# Compatibility for subprocess.run (added in Python 3.5)
def run_subprocess(cmd, timeout=None):
    """Cross-platform subprocess runner for Python 2.7+ compatibility."""
    if hasattr(subprocess, 'run'):
        # Python 3.5+
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    else:
        # Python 2.7, 3.3, 3.4
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        # Create a simple result object similar to subprocess.CompletedProcess
        class Result:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr
        return Result(popen.returncode, stdout, stderr)

def safe_decode(data, encoding='utf-8', errors='replace'):
    """Safe decode for Python 2.7/3.x compatibility."""
    if isinstance(data, bytes):
        try:
            return data.decode(encoding, errors)
        except UnicodeDecodeError:
            return data.decode(encoding, 'replace')
    return data


def test_cli_output_flag_with_unicode():
    """Regression test for GitHub issues #2, #57, #59, #68, #113, #123, #129.

    Tests that the CLI tool can write Unicode characters to files using --output flag.
    This should fail on Windows without proper encoding handling.
    """
    # Minimal source with all problematic Unicode characters from reported issues
    source_code = u'print(u"❌ ✓ 🐍 Привет © ∀")'

    # Create temporary source file
    # Python 2.7 doesn't support encoding parameter, so use binary mode
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as source_file:
        source_file.write(source_code.encode('utf-8'))
        source_path = source_file.name

    # Create temporary output file path
    with tempfile.NamedTemporaryFile(mode='w', suffix='.min.py', delete=False) as output_file:
        output_path = output_file.name

    try:
        # Remove output file so pyminify can create it
        os.unlink(output_path)

        # Run pyminify CLI with --output flag (this should reproduce Windows encoding errors)
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier',
            source_path, '--output', output_path
        ], timeout=30)

        # Test should fail if CLI command fails (indicates Windows encoding bug)
        assert result.returncode == 0, "CLI failed with encoding error: {}".format(safe_decode(result.stderr))

        # Verify the output file was created and contains Unicode characters
        # Python 2.7 doesn't support encoding parameter in open()
        with codecs.open(output_path, 'r', encoding='utf-8') as f:
            minified_content = f.read()

        # Verify problematic Unicode characters are preserved
        if hasattr(sys, 'pypy_version_info') and sys.version_info[0] >= 3:
            # PyPy3: Unicode characters are escaped as \\u escapes
            assert "\\u274c" in minified_content  # ❌ Issue #113
            assert "✓" in minified_content   # Issue #129
            assert "\\U0001f40d" in minified_content  # 🐍 General emoji
            assert "Привет" in minified_content  # Issue #123
            assert "©" in minified_content   # Issue #59
            assert "∀" in minified_content   # Mathematical symbols
        elif hasattr(sys, 'pypy_version_info') and sys.version_info[0] < 3:
            # PyPy2: Unicode characters appear as UTF-8 byte sequences
            assert "\\xe2\\x9d\\x8c" in minified_content  # ❌ Issue #113
            assert "\\xe2\\x9c\\x93" in minified_content  # ✓ Issue #129
            assert "\\xf0\\x9f\\x90\\x8d" in minified_content  # 🐍 General emoji
        elif sys.version_info[0] >= 3:
            # CPython 3: Unicode characters should appear literally  
            assert "❌" in minified_content  # Issue #113
            assert "✓" in minified_content   # Issue #129
            assert "🐍" in minified_content  # General emoji
            assert "Привет" in minified_content  # Issue #123
            assert "©" in minified_content   # Issue #59
            assert "∀" in minified_content   # Mathematical symbols
        else:
            # Python 2.7: Check for escaped sequences or use Unicode literals
            assert u"\\xe2\\x9d\\x8c" in minified_content or u"❌" in minified_content  # ❌
            assert u"\\xe2\\x9c\\x93" in minified_content or u"✓" in minified_content  # ✓ 
            assert u"\\xf0\\x9f\\x90\\x8d" in minified_content or u"🐍" in minified_content  # 🐍

    finally:
        # Cleanup
        if os.path.exists(source_path):
            os.unlink(source_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_cli_in_place_with_unicode():
    """Regression test for --in-place flag with Unicode characters.

    Tests GitHub issues #57, #68 where --in-place fails on Windows.
    """
    source_code = u'print(u"❌ ✓ 🐍 Привет © ∀")'

    # Create temporary file
    # Python 2.7 doesn't support encoding parameter, so use binary mode
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as temp_file:
        temp_file.write(source_code.encode('utf-8'))
        temp_path = temp_file.name

    try:
        # Run pyminify with --in-place flag
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier',
            temp_path, '--in-place'
        ], timeout=30)

        # Test should fail if CLI command fails (indicates Windows encoding bug)
        assert result.returncode == 0, "CLI failed with encoding error: {}".format(safe_decode(result.stderr))

        # Verify Unicode characters are preserved in the modified file
        # Python 2.7 doesn't support encoding parameter in open()
        with codecs.open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if hasattr(sys, 'pypy_version_info') and sys.version_info[0] >= 3:
            # PyPy3: Unicode characters are escaped as \\u escapes  
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
            # Python 2.7: Check for escaped sequences or Unicode literals
            assert u"\\xe2\\x9c\\x93" in content or u"✓" in content  # ✓
            assert u"\\xe2\\x9d\\x8c" in content or u"❌" in content  # ❌
            assert u"\\xf0\\x9f\\x90\\x8d" in content or u"🐍" in content  # 🐍

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_cli_stdout_with_unicode():
    """Verify that stdout output works fine (as reported in issues).

    All GitHub issues mention that stdout output works, only file output fails.
    """
    source_code = u'print(u"❌ ✓ 🐍 Привет © ∀")'

    # Python 2.7 doesn't support encoding parameter, so use binary mode
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as temp_file:
        temp_file.write(source_code.encode('utf-8'))
        temp_path = temp_file.name

    try:
        # Run without --output or --in-place (should output to stdout)
        # Use our compatibility function to avoid subprocess decoding issues with Windows
        # We'll manually decode as UTF-8 to properly handle Unicode characters
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier', temp_path
        ], timeout=30)

        assert result.returncode == 0, "Stdout output failed: {}".format(safe_decode(result.stderr))

        # Decode stdout and verify Unicode characters are present
        stdout_text = safe_decode(result.stdout)
        
        if hasattr(sys, 'pypy_version_info') and sys.version_info[0] >= 3:
            # PyPy3: Unicode characters are escaped as \\u escapes
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
        os.unlink(temp_path)


@pytest.mark.skipif(os.name != 'nt', reason="Windows-specific encoding test")
def test_windows_default_encoding_detection():
    """Test to detect Windows default encoding that causes issues."""

    # Check what encoding Python would use on Windows for file operations
    default_encoding = locale.getpreferredencoding()

    # On problematic Windows systems, this is often cp1252, gbk, or similar
    print("Windows default encoding: {}".format(default_encoding))

    # This test documents the encoding environment for debugging
    assert default_encoding is not None


def test_system_encoding_info():
    """Diagnostic test to understand system encoding setup."""

    print("System default encoding: {}".format(sys.getdefaultencoding()))
    print("Filesystem encoding: {}".format(sys.getfilesystemencoding()))
    print("Preferred encoding: {}".format(locale.getpreferredencoding()))
    print("Platform: {}".format(sys.platform))

    # This test always passes but provides diagnostic information
    assert True

