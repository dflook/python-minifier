import sys

import pytest

from helpers import assert_namespace_tree


def test_class_typevar_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
class Foo[T = str]: ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Foo', allow_rename=True) <references=1>
  - NameBinding(name='T', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=1>
  + Class Foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_function_typevar_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
A = str
def foo[T = A](): ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='A', allow_rename=True) <references=2>
  - NameBinding(name='T', allow_rename=True) <references=1>
  - NameBinding(name='foo', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=1>
  + Function foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_alias_typevar_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
A = str
type Alias[DefaultT = A] = Blah
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='A', allow_rename=True) <references=2>
  - NameBinding(name='Alias', allow_rename=True) <references=1>
  - NameBinding(name='Blah', allow_rename=False) <references=1>
  - NameBinding(name='DefaultT', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_typevartuple_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
T=tuple[str, int]
class Foo[*T = str]: ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Foo', allow_rename=True) <references=1>
  - NameBinding(name='T', allow_rename=True) <references=2>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=2>
  - BuiltinBinding(name='tuple', allow_rename=True) <references=1>
  + Class Foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_function_typevartuple_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
A = tuple[str, int]
def foo[*T = A](): ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='A', allow_rename=True) <references=2>
  - NameBinding(name='T', allow_rename=True) <references=1>
  - NameBinding(name='foo', allow_rename=True) <references=1>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=1>
  - BuiltinBinding(name='tuple', allow_rename=True) <references=1>
  + Function foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_alias_typevartuple_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
type Alias[*DefaultT = tuple[str, int]] = Blah
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Alias', allow_rename=True) <references=1>
  - NameBinding(name='Blah', allow_rename=False) <references=1>
  - NameBinding(name='DefaultT', allow_rename=True) <references=1>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=1>
  - BuiltinBinding(name='tuple', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_paramspec_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
T=tuple[str, int]
class Foo[**T = str]: ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Foo', allow_rename=True) <references=1>
  - NameBinding(name='T', allow_rename=True) <references=2>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=2>
  - BuiltinBinding(name='tuple', allow_rename=True) <references=1>
  + Class Foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_function_paramspec_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
A = tuple[str, int]
def foo[**T = A](): ...
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='A', allow_rename=True) <references=2>
  - NameBinding(name='T', allow_rename=True) <references=1>
  - NameBinding(name='foo', allow_rename=True) <references=1>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=1>
  - BuiltinBinding(name='tuple', allow_rename=True) <references=1>
  + Function foo
'''

    assert_namespace_tree(source, expected_namespaces)


def test_alias_paramspec_default():
    if sys.version_info < (3, 13):
        pytest.skip('Test is for python3.13 only')

    source = '''
type Alias[**DefaultT = tuple[str, int]] = Blah
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Alias', allow_rename=True) <references=1>
  - NameBinding(name='Blah', allow_rename=False) <references=1>
  - NameBinding(name='DefaultT', allow_rename=True) <references=1>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  - BuiltinBinding(name='str', allow_rename=True) <references=1>
  - BuiltinBinding(name='tuple', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)
