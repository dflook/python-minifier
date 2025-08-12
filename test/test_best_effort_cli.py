"""Tests for CLI size-based output selection (best effort) functionality."""
import os
import sys
import tempfile

from subprocess_compat import run_subprocess, safe_decode


def test_returns_minified_when_smaller():
    """Test CLI returns minified output when it's smaller than original."""
    code = '''
def hello_world():
    """A simple function."""
    print("Hello, world!")
    return None

if __name__ == "__main__":
    hello_world()
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        env = os.environ.copy()
        env.pop('PYMINIFY_FORCE_BEST_EFFORT', None)
        
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier', temp_file
        ], timeout=30, env=env)
        
        assert result.returncode == 0
        
        stdout_text = safe_decode(result.stdout)
        assert len(stdout_text) < len(code)
        
    finally:
        os.unlink(temp_file)


def test_returns_original_when_longer():
    """Test CLI returns original code when minified output would be longer."""
    code = 'True if 0in x else False'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        env = os.environ.copy()
        env.pop('PYMINIFY_FORCE_BEST_EFFORT', None)
        
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier', temp_file
        ], timeout=30, env=env)
        
        assert result.returncode == 0
        
        stdout_text = safe_decode(result.stdout)
        assert stdout_text == code
        
    finally:
        os.unlink(temp_file)


def test_force_minified_with_env_var():
    """Test environment variable forces minified output regardless of size."""
    code = 'True if 0in x else False'
    expected_output = 'True if 0 in x else False'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        env = os.environ.copy()
        env['PYMINIFY_FORCE_BEST_EFFORT'] = '1'
        
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier', temp_file
        ], timeout=30, env=env)
        
        assert result.returncode == 0
        
        stdout_text = safe_decode(result.stdout)
        assert stdout_text == expected_output
        
    finally:
        os.unlink(temp_file)


def test_stdin_behavior():
    """Test size-based logic works with stdin input."""
    code = 'True if 0in x else False'
    expected_output = 'True if 0 in x else False'
    
    # Without env var - should return original
    env = os.environ.copy()
    env.pop('PYMINIFY_FORCE_BEST_EFFORT', None)
    
    result = run_subprocess([
        sys.executable, '-m', 'python_minifier', '-'
    ], input_data=code, timeout=30, env=env)
    
    assert result.returncode == 0
    stdout_text = safe_decode(result.stdout)
    assert stdout_text == code
    
    # With env var - should return minified
    env['PYMINIFY_FORCE_BEST_EFFORT'] = '1'
    
    result = run_subprocess([
        sys.executable, '-m', 'python_minifier', '-'
    ], input_data=code, timeout=30, env=env)
    
    assert result.returncode == 0
    stdout_text = safe_decode(result.stdout)
    assert stdout_text == expected_output


def test_output_file_behavior():
    """Test size-based logic works with --output flag."""
    code = 'True if 0in x else False'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as input_file:
        input_file.write(code)
        input_filename = input_file.name
    
    with tempfile.NamedTemporaryFile(delete=False) as output_file:
        output_filename = output_file.name
    
    try:
        env = os.environ.copy()
        env.pop('PYMINIFY_FORCE_BEST_EFFORT', None)
        
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier',
            input_filename, '--output', output_filename
        ], timeout=30, env=env)
        
        assert result.returncode == 0
        
        with open(output_filename, 'r') as f:
            output_content = f.read()
        
        assert output_content == code
        
    finally:
        os.unlink(input_filename)
        os.unlink(output_filename)


def test_in_place_behavior():
    """Test size-based logic works with --in-place flag."""
    code = 'True if 0in x else False'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        env = os.environ.copy()
        env.pop('PYMINIFY_FORCE_BEST_EFFORT', None)
        
        result = run_subprocess([
            sys.executable, '-m', 'python_minifier',
            temp_file, '--in-place'
        ], timeout=30, env=env)
        
        assert result.returncode == 0
        
        with open(temp_file, 'r') as f:
            modified_content = f.read()
        
        assert modified_content == code
        
    finally:
        os.unlink(temp_file)