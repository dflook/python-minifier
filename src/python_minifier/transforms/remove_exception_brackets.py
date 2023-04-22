"""
Remove Call nodes that are only used to raise exceptions with no arguments

If a Raise statement is used on a Name and the name refers to an exception, it is automatically instantiated with no arguments
We can remove any Call nodes that are only used to raise exceptions with no arguments and let the Raise statement do the instantiation.
When printed, this essentially removes the brackets from the exception name.

We can't generally know if a name refers to an exception, so we only do this for builtin exceptions
"""

import ast

from python_minifier.rename.binding import BuiltinBinding

# This list may vary between python versions
builtin_exceptions = [
    'BaseException',
    'BaseExceptionGroup',
    'GeneratorExit',
    'KeyboardInterrupt',
    'SystemExit',
    'Exception',
    'ArithmeticError',
    'FloatingPointError',
    'OverflowError',
    'ZeroDivisionError',
    'AssertionError',
    'AttributeError',
    'BufferError',
    'EOFError',
    'ExceptionGroup',
    'BaseExceptionGroup',
    'ImportError',
    'ModuleNotFoundError',
    'LookupError',
    'IndexError',
    'KeyError',
    'MemoryError',
    'NameError',
    'UnboundLocalError',
    'OSError',
    'BlockingIOError',
    'ChildProcessError',
    'ConnectionError',
    'BrokenPipeError',
    'ConnectionAbortedError',
    'ConnectionRefusedError',
    'ConnectionResetError',
    'FileExistsError',
    'FileNotFoundError',
    'InterruptedError',
    'IsADirectoryError',
    'NotADirectoryError',
    'PermissionError',
    'ProcessLookupError',
    'TimeoutError',
    'ReferenceError',
    'RuntimeError',
    'NotImplementedError',
    'RecursionError',
    'StopAsyncIteration',
    'StopIteration',
    'SyntaxError',
    'IndentationError',
    'TabError',
    'SystemError',
    'TypeError',
    'ValueError',
    'UnicodeError',
    'UnicodeDecodeError',
    'UnicodeEncodeError',
    'UnicodeTranslateError',
    'Warning',
    'BytesWarning',
    'DeprecationWarning',
    'EncodingWarning',
    'FutureWarning',
    'ImportWarning',
    'PendingDeprecationWarning',
    'ResourceWarning',
    'RuntimeWarning',
    'SyntaxWarning',
    'UnicodeWarning',
    'UserWarning'
]

def _remove_empty_call(binding):
    assert isinstance(binding, BuiltinBinding)

    for name_node in binding.references:
        assert isinstance(name_node, ast.Name)  # For this to be a builtin, all references must be name nodes as it is not defined anywhere

        if not isinstance(name_node.parent, ast.Call):
            # This is not a call
            continue
        call_node = name_node.parent

        if not isinstance(call_node.parent, ast.Raise):
            # This is not a raise statement
            continue
        raise_node = call_node.parent

        if len(call_node.args) > 0 or len(call_node.keywords) > 0:
            # This is a call with arguments
            continue

        # This is an instance of the exception being called with no arguments
        # let's replace it with just the name, cutting out the Call node

        if raise_node.exc is call_node:
            raise_node.exc = name_node
        elif raise_node.cause is call_node:
            raise_node.cause = name_node
        name_node.parent = raise_node

def remove_no_arg_exception_call(module):
    assert isinstance(module, ast.Module)

    for binding in module.bindings:
        if isinstance(binding, BuiltinBinding) and binding.name in builtin_exceptions:
            # We can remove any calls to builtin exceptions
            _remove_empty_call(binding)
