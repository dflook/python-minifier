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
