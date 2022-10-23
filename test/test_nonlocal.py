import sys

import pytest

import python_minifier

def test_nonlocal_name():
    if sys.version_info < (3, 0):
        pytest.skip('No nonlocal in python < 3.0')

    test_code = '''
def test():
    def outer():
        def inner():
            nonlocal rename_me
            rename_me = 'inner'

        inner()
    rename_me = False        
    outer()
    return rename_me

result = test()
    '''

    # First check we understand the behavior
    unminified_locals = {}
    exec(test_code, {}, unminified_locals)
    assert unminified_locals['result'] == 'inner'

    minified = python_minifier.minify(test_code, rename_locals=True)
    print(minified)
    minified_locals = {}
    exec(minified, {}, minified_locals)
    assert minified_locals['result'] == 'inner'


def test_nonlocal_def():
    if sys.version_info < (3, 0):
        pytest.skip('No nonlocal in python < 3.0')

    test_code = '''
def test():
    def patch():
        nonlocal f
        f = lambda: 2

    def f():
        return 1
        
    patch()
    return f()

result = test()
    '''

    # First check we understand the behavior
    unminified_locals = {}
    exec(test_code, {}, unminified_locals)
    assert unminified_locals['result'] == 2

    minified = python_minifier.minify(test_code, rename_locals=True)
    print(minified)
    minified_locals = {}
    exec(minified, {}, minified_locals)
    assert minified_locals['result'] == 2

def test_nonlocal_import():
    if sys.version_info < (3, 0):
        pytest.skip('No nonlocal in python < 3.0')

    test_code = '''
def test():

    def patch():
        nonlocal hashlib
        import hashlib

    hashlib = None
    patch()
    return 'sha256' in hashlib.algorithms_available

result = test()
    '''

    # First check we understand the behavior
    unminified_locals = {}
    exec(test_code, {}, unminified_locals)
    assert unminified_locals['result'] == True

    minified = python_minifier.minify(test_code, rename_locals=True)
    print(minified)
    minified_locals = {}
    exec(minified, {}, minified_locals)
    assert minified_locals['result'] == True

def test_nonlocal_import_alias():
    if sys.version_info < (3, 0):
        pytest.skip('No nonlocal in python < 3.0')

    test_code = '''
def test():

    def patch():
        nonlocal a
        import hashlib as a

    a = None
    patch()
    return 'sha256' in a.algorithms_available

result = test()
    '''

    # First check we understand the behavior
    unminified_locals = {}
    exec(test_code, {}, unminified_locals)
    assert unminified_locals['result'] == True

    minified = python_minifier.minify(test_code, rename_locals=True)
    print(minified)
    minified_locals = {}
    exec(minified, {}, minified_locals)
    assert minified_locals['result'] == True
