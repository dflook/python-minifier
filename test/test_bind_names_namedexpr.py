import sys

import pytest

from helpers import assert_namespace_tree

def test_namedexpr_in_module():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

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
        pytest.skip('Test is for >= python3.8 only')

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

def test_namedexpr_in_listcomp_if_nonlocal():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
def f(arg, /):
  nonlocal x
  print([x for y in range(10) if (x := y // 2) & 1])
  print(arg, arg)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='f', allow_rename=True) <references=1>
  - BuiltinBinding(name='print', allow_rename=True) <references=2>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=False) <references=3>
  + Function f
    - nonlocal x
    - NameBinding(name='arg', allow_rename=True) <references=3>
    + ListComp
      - NameBinding(name='y', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_namedexpr_in_listcomp_if_global():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
def f2():
    def f(arg, /):
      global x
      print([x for y in range(10) if (x := y // 2) & 1])
      print(arg, arg)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='f2', allow_rename=True) <references=1>
  - BuiltinBinding(name='print', allow_rename=True) <references=2>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=3>
  + Function f2
    - NameBinding(name='f', allow_rename=True) <references=1>
    + Function f
      - global x
      - NameBinding(name='arg', allow_rename=True) <references=3>
      + ListComp
        - NameBinding(name='y', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_namedexpr_in_listcomp_if():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

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


def test_namedexpr_in_listcomp_body():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
def f(arg, /):
  print([(x := y // 2) for _ in range(x)])
  print(arg, arg)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='f', allow_rename=True) <references=1>
  - BuiltinBinding(name='print', allow_rename=True) <references=2>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='y', allow_rename=False) <references=1>
  + Function f
    - NameBinding(name='arg', allow_rename=True) <references=3>
    - NameBinding(name='x', allow_rename=True) <references=2>
    + ListComp
      - NameBinding(name='_', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_namedexpr_in_dictcomp_body():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
{i: (x := i // 2) for i in range(1)}
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=1>
  + DictComp
    - NameBinding(name='i', allow_rename=True) <references=3>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_namedexpr_in_dictcomp_if():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
{x: y for y in range(1) if (x := y // 2)}
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=2>
  + DictComp
    - NameBinding(name='y', allow_rename=True) <references=3>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_namedexpr_in_setcomp_body():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
{(x := y // 2) for y in range(1)}
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=1>
  + SetComp
    - NameBinding(name='y', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_namedexpr_in_setcomp_if():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
{x for y in range(1) if (x := y // 2)}
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=2>
  + SetComp
    - NameBinding(name='y', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_namedexpr_in_generatorexp_body():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
((x := y // 2) for y in range(1))
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=1>
  + GeneratorExp
    - NameBinding(name='y', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_namedexpr_in_generatorexp_if():
    if sys.version_info < (3, 8):
        pytest.skip('Test is for >= python3.8 only')

    source = '''
(x for y in range(1) if (x := y // 2))
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=2>
  + GeneratorExp
    - NameBinding(name='y', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)
