import ast
import sys

import pytest

from python_minifier.compat import find_syntax_versions

def test_no_special_syntax():
    source = '''
a = 'Hello'
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((2, 7), sys.version_info[:2])

def test_named_expr():
    if sys.version_info < (3, 8):
        pytest.skip('Python < 3.8 does not have named expressions')

    source = '''
if a := 1:
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 8), sys.version_info[:2])

def test_matmult():
    if sys.version_info < (3, 5):
        pytest.skip('Python < 3.5 does not have matmult')

    source = '''
a @ b
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 5), sys.version_info[:2])

def test_annassign():
    if sys.version_info < (3, 6):
        pytest.skip('Python < 3.6 does not have annotated assignments')

    source = '''
a: int = 1
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 6), sys.version_info[:2])

def test_kwonlyargs():
    if sys.version_info < (3, 0):
        pytest.skip('Python 2 does not have kwonlyargs')

    source = '''
def f(a, b, *, c):
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 0), sys.version_info[:2])

def test_posonlyargs():
    if sys.version_info < (3, 8):
        pytest.skip('Python < 3.8 does not have posonlyargs')

    source = '''
def f(a, b, /, c):
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 8), sys.version_info[:2])

def test_vararg_annotation():
    if sys.version_info < (3, 0):
        pytest.skip('Python < 3.0 does not have annotations')

    source = '''
def f(*args: int):
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 0), sys.version_info[:2])

def test_kwarg_annotation():
    if sys.version_info < (3, 0):
        pytest.skip('Python < 3.0 does not have annotations')

    source = '''
def f(**kwargs: int):
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 0), sys.version_info[:2])

def test_arg_annotation():
    if sys.version_info < (3, 0):
        pytest.skip('Python < 3.0 does not have annotations')

    source = '''
def f(a: int):
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 0), sys.version_info[:2])

def test_nonlocal():
    if sys.version_info < (3, 0):
        pytest.skip('Python < 3.0 does not have nonlocal')

    source = '''
def f():
    nonlocal a
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 0), sys.version_info[:2])

def test_async_function():
    if sys.version_info < (3, 5):
        pytest.skip('Python < 3.5 does not have async functions')

    source = '''
async def f():
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 5), sys.version_info[:2])

def test_async_with():
    if sys.version_info < (3, 5):
        pytest.skip('Python < 3.5 does not have async with')

    source = '''
async with a:
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 5), sys.version_info[:2])

def test_async_for():
    if sys.version_info < (3, 5):
        pytest.skip('Python < 3.5 does not have async for')

    source = '''
async for a in b:
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 5), sys.version_info[:2])

def test_async_comprehension():
    if sys.version_info < (3, 6):
        pytest.skip('Python < 3.6 does not have async comprehensions')

    source = '''
[a async for a in b]
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 6), sys.version_info[:2])

def test_await():
    if sys.version_info < (3, 5):
        pytest.skip('Python < 3.5 does not have await')

    source = '''
await a
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 5), sys.version_info[:2])

def test_match():
    if sys.version_info < (3, 10):
        pytest.skip('Python < 3.10 does not have match')

    source = '''
match a:
    case b:
        pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 10), sys.version_info[:2])

def test_repr():
    if sys.version_info > (2, 7):
        pytest.skip('Python 3 does not have backtick syntax')

    source = '''
`1+2`
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((2, 7), (2,7))

def test_try_star():
    if sys.version_info < (3, 11):
        pytest.skip('Python < 3.11 does not have try star')

    source = '''
try:
    pass
except* Error as e:
    pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 11), sys.version_info[:2])

def test_function_type_var():
    if sys.version_info < (3, 12):
        pytest.skip('Python < 3.12 does not have type vars')

    source = '''
def a[T](): pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 12), sys.version_info[:2])

def test_class_type_var():
    if sys.version_info < (3, 12):
        pytest.skip('Python < 3.12 does not have type vars')

    source = '''
class a[T]: pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 12), sys.version_info[:2])

def test_typevar_tuple():
    if sys.version_info < (3, 12):
        pytest.skip('Python < 3.12 does not have type vars')

    source = '''
class a[*T]: pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 12), sys.version_info[:2])

def test_paramspec():
    if sys.version_info < (3, 12):
        pytest.skip('Python < 3.12 does not have type vars')

    source = '''
class a[**T]: pass
'''

    min_version, max_version = find_syntax_versions(ast.parse(source))
    assert min_version, max_version == ((3, 12), sys.version_info[:2])