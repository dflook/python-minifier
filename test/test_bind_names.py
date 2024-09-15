import sys

import pytest

from helpers import assert_namespace_tree


def test_module_namespace():
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

    source = '''
name_in_module = True
name_in_module = True
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='name_in_module', allow_rename=True) <references=2>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_lambda_namespace():
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

    source = '''
name_in_module = True

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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

def test_async_function_namespace():
    if sys.version_info < (3, 5):
        pytest.skip('No async functions in python < 3.5')

    source = '''
name_in_module = True

async def func(arg, *args, **kwargs):
    name_in_func = True
    print(name_in_module)

    async def inner_func():
        print(name_in_module)
        name_in_inner_func = True
'''

    expected_namespaces = '''
+ Module
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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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
    if sys.version_info < (3, 6):
        pytest.skip('Annotations are not available in python < 3.6')

    source = '''
OhALongName = 'Hello'
OhALongName = 'Hello'
MyOtherName = 'World'

def func():
  class C:
    OhALongName = ' World'
    MyOtherName = OhALongName
    ClassName: int

func()
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='MyOtherName', allow_rename=True) <references=1>
  - NameBinding(name='OhALongName', allow_rename=False) <references=4>
  - NameBinding(name='func', allow_rename=True) <references=2>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  + Function func
    - NameBinding(name='C', allow_rename=True) <references=1>
    + Class C
      - nonlocal OhALongName
      - nonlocal int
      - NameBinding(name='ClassName', allow_rename=False) <references=1>
      - NameBinding(name='MyOtherName', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_name_rebinding():
    if sys.version_info < (3, 4):
        pytest.skip('Test requires python 3.4 or later')

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

def test_class_namespace_nonlocal_name_allow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=True) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_name_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=1>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_builtin_name_allow_rename():
    source = '''
class LazyList:
    MyAttribute = int

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - BuiltinBinding(name='int', allow_rename=True) <references=1>
  + Class LazyList
    - nonlocal int
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_builtin_name_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = int
    int = 1

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - BuiltinBinding(name='int', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal int
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_namespace_nonlocal_non_builtin_name_disallow_rename():
    if sys.version_info < (3, 4):
        pytest.skip('NameConstants are different in python < 3.4')

    source = '''
int = None
class LazyList:
    MyAttribute = int

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='int', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal int
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_name_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    MyNonLocal = 2

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_name_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    MyNonLocal = 2
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_import_as_disallow_rename():
    """import os as MyNonLocal"""
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    import os as MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_import_as_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    import os as MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_import_from_as_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    from os import Hello as MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_import_from_as_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    from os import Hello as MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_import_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    import MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_import_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    import MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_import_from_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    from Hello import MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_import_from_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    from Hello import MyNonLocal

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_dotted_import_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    import MyNonLocal.Hello

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_dotted_import_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    import MyNonLocal.Hello

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_func_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    def MyNonLocal(): pass

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
    + Function MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_func_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    def MyNonLocal(): pass

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
    + Function MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_async_func_disallow_rename():
    if sys.version_info < (3, 5):
        pytest.skip('No async functions in python < 3.5')

    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    async def MyNonLocal(): pass

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
    + Function MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_async_func_disallow_rename():
    if sys.version_info < (3, 5):
        pytest.skip('No async functions in python < 3.5')

    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    async def MyNonLocal(): pass

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
    + Function MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_classdef_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    class MyNonLocal(): pass

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
    + Class MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_classdef_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    class MyNonLocal(): pass

'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
    + Class MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_namespace_nonlocal_except_disallow_rename():
    source = '''
MyNonLocal = 1

class LazyList:
    MyAttribute = MyNonLocal
    try:
        pass
    except Exception as MyNonLocal:
        pass

'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='Exception', allow_rename=True) <references=1>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal Exception
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_except_disallow_rename():
    source = '''
class LazyList:
    MyAttribute = MyNonLocal
    try:
        pass
    except Exception as MyNonLocal:
        pass        

'''

    expected_namespaces = '''
+ Module
  - BuiltinBinding(name='Exception', allow_rename=True) <references=1>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal Exception
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)


def test_class_namespace_nonlocal_match_disallow_rename():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
MyNonLocal = 1
Blah = "Hello"
    
class LazyList:
    MyAttribute = MyNonLocal
    match Blah:
        case MyNonLocal:
            pass
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Blah', allow_rename=True) <references=2>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal Blah
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_match_disallow_rename():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
Blah = "Hello"
class LazyList:
    MyAttribute = MyNonLocal
    match Blah:
        case MyNonLocal:
            pass  
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Blah', allow_rename=True) <references=2>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal Blah
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_match_star_disallow_rename():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
MyNonLocal = 1
Blah = "Hello"

class LazyList:
    MyAttribute = MyNonLocal
    match Blah:
        case [*MyNonLocal]:
            pass
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Blah', allow_rename=True) <references=2>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal Blah
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_match_star_disallow_rename():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
Blah = "Hello"
class LazyList:
    MyAttribute = MyNonLocal
    match Blah:
        case [*MyNonLocal]:
            pass  
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Blah', allow_rename=True) <references=2>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal Blah
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_match_mapping_disallow_rename():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
MyNonLocal = 1
Blah = "Hello"

class LazyList:
    MyAttribute = MyNonLocal
    match Blah:
        case {**MyNonLocal}:
            pass
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Blah', allow_rename=True) <references=2>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=3>
  + Class LazyList
    - nonlocal Blah
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_match_mapping_disallow_rename():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
Blah = "Hello"
class LazyList:
    MyAttribute = MyNonLocal
    match Blah:
        case {**MyNonLocal}:
            pass  
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='Blah', allow_rename=True) <references=2>
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal Blah
    - nonlocal MyNonLocal
    - NameBinding(name='MyAttribute', allow_rename=False) <references=1>
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_nonlocal_disallow_rename():
    if sys.version_info < (3, 0):
        pytest.skip('nonlocal in class is invalid in Python 2')

    source = '''
MyNonLocal = 1

class LazyList:
    nonlocal MyNonLocal
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=2>
  + Class LazyList
    - nonlocal MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)

def test_class_namespace_undefined_nonlocal_disallow_rename():
    if sys.version_info < (3, 0):
        pytest.skip('nonlocal in class is invalid in Python 2')

    source = '''
class LazyList:
    nonlocal MyNonLocal
'''

    expected_namespaces = '''
+ Module
  - NameBinding(name='LazyList', allow_rename=True) <references=1>
  - NameBinding(name='MyNonLocal', allow_rename=False) <references=1>
  + Class LazyList
    - nonlocal MyNonLocal
'''

    assert_namespace_tree(source, expected_namespaces)
