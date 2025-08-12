"""Subprocess compatibility utilities for Python 2.7/3.x."""
import subprocess
import sys


def run_subprocess(cmd, timeout=None, input_data=None, env=None):
    """Cross-platform subprocess runner for Python 2.7+ compatibility."""
    if hasattr(subprocess, 'run'):
        # Python 3.5+ - encode string input to bytes for subprocess
        input_bytes = input_data.encode('utf-8') if isinstance(input_data, str) else input_data
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                            input=input_bytes, timeout=timeout, env=env)
    else:
        # Python 2.7, 3.3, 3.4 - no subprocess.run, no timeout support
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               stdin=subprocess.PIPE if input_data else None, env=env)
        # For Python 3.3/3.4, communicate() doesn't support timeout
        # Also, Python 3.x needs bytes for stdin, Python 2.x needs str
        if input_data and sys.version_info[0] >= 3 and isinstance(input_data, str):
            input_data = input_data.encode('utf-8')
        stdout, stderr = popen.communicate(input_data)
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