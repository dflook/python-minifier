import sys

import pytest

from helpers import assert_namespace_tree


def test_class_typevar_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
class Foo[T]: ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Foo', allow_rename=True) <references=1>
  - NameBinding(name='T', allow_rename=True) <references=1>
  + Class Foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_function_typevar_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
def foo[T](): ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='T', allow_rename=True) <references=1>
  - NameBinding(name='foo', allow_rename=True) <references=1>
  + Function foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_alias_typevar_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
type Alias[DefaultT] = Blah
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Alias', allow_rename=True) <references=1>
  - NameBinding(name='Blah', allow_rename=False) <references=1>
  - NameBinding(name='DefaultT', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_typevartuple_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
class Foo[*T]: ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Foo', allow_rename=True) <references=1>
  - NameBinding(name='T', allow_rename=True) <references=1>
  + Class Foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_function_typevartuple_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
def foo[*T](): ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='T', allow_rename=True) <references=1>
  - NameBinding(name='foo', allow_rename=True) <references=1>
  + Function foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_alias_typevartuple_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
type Alias[*DefaultT] = Blah
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Alias', allow_rename=True) <references=1>
  - NameBinding(name='Blah', allow_rename=False) <references=1>
  - NameBinding(name='DefaultT', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_paramspec_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
class Foo[**T]: ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Foo', allow_rename=True) <references=1>
  - NameBinding(name='T', allow_rename=True) <references=1>
  + Class Foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_function_paramspec_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
def foo[**T](): ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='T', allow_rename=True) <references=1>
  - NameBinding(name='foo', allow_rename=True) <references=1>
  + Function foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_alias_paramspec_default():
    if sys.version_info < (3, 12):
        pytest.skip('Test is for > python3.12 only')

    source = '''
type Alias[**DefaultT] = Blah
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Alias', allow_rename=True) <references=1>
  - NameBinding(name='Blah', allow_rename=False) <references=1>
  - NameBinding(name='DefaultT', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_namedexpr_in_module():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for > python3.8 only')

    source = '''
(a := 1)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_namedexpr_in_function():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for > python3.8 only')

    source = '''
def test():
    (a := 1)
lambda x: (x := 1)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='test', allow_rename=True) <references=1>
  + Function test
    - NameBinding(name='a', allow_rename=True) <references=1>
  + Lambda
    - NameBinding(name='x', allow_rename=False) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_namedexpr():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for > python3.8 only')

    source = '''
def f(arg, /):
  print([x for y in range(10) if (x := y // 2) & 1])
  print(arg, arg)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='f', allow_rename=True) <references=1>
  - BuiltinBinding(name='print', allow_rename=True) <references=2>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  + Function f
    - NameBinding(name='arg', allow_rename=True) <references=3>
    - NameBinding(name='x', allow_rename=True) <references=2>
    + ListComp
      - NameBinding(name='y', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)
