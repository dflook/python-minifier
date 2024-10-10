import sys

import pytest

from helpers import assert_namespace_tree


def test_module_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
name_in_module = True
name_in_module = True
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='True', allow_rename=True) <references=2>
  - NameBinding(name='name_in_module', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_lambda_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
name_in_module = 0

b = lambda arg, *args, **kwargs: arg + 1
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='b', allow_rename=True) <references=1>
  - NameBinding(name='name_in_module', allow_rename=True) <references=1>
  + Lambda
    - NameBinding(name='arg', allow_rename=False) <references=2>
    - NameBinding(name='args', allow_rename=True) <references=1>
    - NameBinding(name='kwargs', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_function_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
name_in_module = True

def func(arg, *args, **kwargs):
    name_in_func = True
    print(name_in_module)

    def inner_func():
        print(name_in_module)
        name_in_inner_func = True
'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='True', allow_rename=True) <references=3>
  - NameBinding(name='func', allow_rename=True) <references=1>
  - NameBinding(name='name_in_module', allow_rename=True) <references=3>
  - BuiltinBinding(name='print', allow_rename=True) <references=2>
  + Function func
    - NameBinding(name='arg', allow_rename=True) <references=1>
    - NameBinding(name='args', allow_rename=True) <references=1>
    - NameBinding(name='inner_func', allow_rename=True) <references=1>
    - NameBinding(name='kwargs', allow_rename=True) <references=1>
    - NameBinding(name='name_in_func', allow_rename=True) <references=1>
    + Function inner_func
      - NameBinding(name='name_in_inner_func', allow_rename=True) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


# region generator namespace

def test_generator_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
a = (x for x in range(10))
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  + GeneratorExp
    - NameBinding(name='x', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_generator_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = []
f = []
a = (x for x in f for x in x)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='f', allow_rename=True) <references=2>
  - NameBinding(name='x', allow_rename=True) <references=1>
  + GeneratorExp
    - NameBinding(name='x', allow_rename=True) <references=4>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_generator_namespace_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a = (c for line in file for c in line)
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + GeneratorExp
    - NameBinding(name='c', allow_rename=True) <references=2>
    - NameBinding(name='line', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_generator():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a = (c for c in (line for line in file))
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + GeneratorExp
    - NameBinding(name='c', allow_rename=True) <references=2>
    + GeneratorExp
      - NameBinding(name='line', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_generator_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = ''
a = (x for x in (x for x in x))
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=2>
  + GeneratorExp
    - NameBinding(name='x', allow_rename=True) <references=2>
    + GeneratorExp
      - NameBinding(name='x', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


# endregion


# region setcomp

def test_setcomp_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
a = {x for x in range(10)}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  + SetComp
    - NameBinding(name='x', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_setcomp_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = []
f = []
a = {x for x in f for x in x}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='f', allow_rename=True) <references=2>
  - NameBinding(name='x', allow_rename=True) <references=1>
  + SetComp
    - NameBinding(name='x', allow_rename=True) <references=4>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_setcomp_namespace_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a = {c for line in file for c in line}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + SetComp
    - NameBinding(name='c', allow_rename=True) <references=2>
    - NameBinding(name='line', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_setcomp():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a = {c for c in {line for line in file}}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + SetComp
    - NameBinding(name='c', allow_rename=True) <references=2>
    + SetComp
      - NameBinding(name='line', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_setcomp_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = ''
a = {x for x in {x for x in x}}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=2>
  + SetComp
    - NameBinding(name='x', allow_rename=True) <references=2>
    + SetComp
      - NameBinding(name='x', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


# endregion

# region listcomp

def test_listcomp_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
a = [x for x in range(10)]
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  + ListComp
    - NameBinding(name='x', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_listcomp_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = []
f = []
a = [x for x in f for x in x]
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='f', allow_rename=True) <references=2>
  - NameBinding(name='x', allow_rename=True) <references=1>
  + ListComp
    - NameBinding(name='x', allow_rename=True) <references=4>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_listcomp_namespace_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a = [c for line in file for c in line]
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + ListComp
    - NameBinding(name='c', allow_rename=True) <references=2>
    - NameBinding(name='line', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_listcomp():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a =[c for c in [line for line in file]]
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + ListComp
    - NameBinding(name='c', allow_rename=True) <references=2>
    + ListComp
      - NameBinding(name='line', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_listcomp_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = ''
a =[x for x in [x for x in x]]
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=2>
  + ListComp
    - NameBinding(name='x', allow_rename=True) <references=2>
    + ListComp
      - NameBinding(name='x', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)


# endregion

# region dictcomp

def test_dictcomp_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
a = {x: x for x in range(10)}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - BuiltinBinding(name='range', allow_rename=True) <references=1>
  + DictComp
    - NameBinding(name='x', allow_rename=True) <references=3>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_dictcomp_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = []
f = []
a = {x: x for x, x in f for x, x in x}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='f', allow_rename=True) <references=2>
  - NameBinding(name='x', allow_rename=True) <references=1>
  + DictComp
    - NameBinding(name='x', allow_rename=True) <references=7>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_multi_dictcomp_namespace_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a = {c: c for line, line in file for c, c in line}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + DictComp
    - NameBinding(name='c', allow_rename=True) <references=4>
    - NameBinding(name='line', allow_rename=True) <references=3>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_dictcomp():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
c = ''
line = ''
file = []
a = {c: c for c, c in {line: line for line in file}}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='c', allow_rename=True) <references=1>
  - NameBinding(name='file', allow_rename=True) <references=2>
  - NameBinding(name='line', allow_rename=True) <references=1>
  + DictComp
    - NameBinding(name='c', allow_rename=True) <references=4>
    + DictComp
      - NameBinding(name='line', allow_rename=True) <references=3>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_nested_dictcomp_2():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
x = {}
a = {x:x  for x, x in {x: x for x in x}}
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='a', allow_rename=True) <references=1>
  - NameBinding(name='x', allow_rename=True) <references=2>
  + DictComp
    - NameBinding(name='x', allow_rename=True) <references=4>
    + DictComp
      - NameBinding(name='x', allow_rename=True) <references=3>
'''

    assert_namespace_tree(source, expected_namespaces)


# endregion

def test_class_namespace():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
OhALongName = 'Hello'
OhALongName = 'Hello'
MyOtherName = 'World'

def func():
  class C:
    OhALongName = ' World'
    MyOtherName = OhALongName
    ClassName = 0

func()
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='MyOtherName', allow_rename=True) <references=1>
  - NameBinding(name='OhALongName', allow_rename=False) <references=4>
  - NameBinding(name='func', allow_rename=True) <references=2>
  + Function func
    - NameBinding(name='C', allow_rename=True) <references=1>
    + Class C
      - nonlocal OhALongName
      - NameBinding(name='ClassName', allow_rename=False) <references=1>
      - NameBinding(name='MyOtherName', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_name_rebinding():
    if sys.version_info < (3, 3) or sys.version_info > (3, 4):
        pytest.skip('Test is for python3.3 only')

    source = '''
OhALongName = 'Hello'
OhALongName = 'Hello'
MyOtherName = 'World'

def func():
  class C:
    OhALongName = OhALongName + ' World'
    MyOtherName = OhALongName


func()
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='MyOtherName', allow_rename=True) <references=1>
  - NameBinding(name='OhALongName', allow_rename=False) <references=5>
  - NameBinding(name='func', allow_rename=True) <references=2>
  + Function func
    - NameBinding(name='C', allow_rename=True) <references=1>
    + Class C
      - nonlocal OhALongName
      - NameBinding(name='MyOtherName', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)
