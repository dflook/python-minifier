import ast
import sys

import pytest

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.dead_code import eliminate_dead_code


def remove_unused_variables(source):
    module = ast.parse(source, 'remove_unused_variables')

    add_parent(module)
    add_namespace(module)
    return eliminate_dead_code(module, remove_imports=False, remove_variables=True, remove_definitions=False, remove_unreachable=False)


def run_test(source, expected):
    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_variables(source)
    compare_ast(expected_ast, actual_ast)


def test_unused_variable():
    run_test('''
x = 42
print(1)
''', 'print(1)')


def test_used_variable():
    source = '''
x = 42
print(x)
'''
    run_test(source, source)


def test_side_effect_free_values():
    run_test('''
a = 'text'
b = [1, 2, {3: (4, 5)}]
c = 1 + 2 * 3
d = not a
e = 1 if a else 2
f = a.attribute
g = a[1:2]
h = lambda: 1
i = len
j = a and b or c
k = a < b
print(1)
''', 'print(1)')


def test_values_with_side_effects_are_kept():
    source = '''
a = call()
b = [call()]
c = {1: call()}
d = 1 + call()
e = [i for i in range(3)]
f = a.method()
g = lambda x=call(): x
'''
    run_test(source, source)


@pytest.mark.skipif(sys.version_info < (3, 5), reason='unpacking in displays needs python 3.5')
def test_keeps_value_that_unpacks():
    source = '''
a = [*b]
c = {**d}
'''
    run_test(source, source)


@pytest.mark.skipif(sys.version_info < (3, 6), reason='f-strings and annotated assignments need python 3.6')
def test_f_string_value():
    run_test('''
a = f'{b}'
c = f'{call()}'
print(1)
''', '''
c = f'{call()}'
print(1)
''')


@pytest.mark.skipif(sys.version_info < (3, 5), reason='async functions need python 3.5')
def test_await_and_yield_values_are_kept():
    source = '''
async def f():
    x = await call()
def g():
    y = yield 1
'''
    run_test(source, source)


@pytest.mark.skipif(sys.version_info < (3, 6), reason='annotated assignments need python 3.6')
def test_annotated_assignment():
    run_test('''
x: int = 42
y: int
z: int = call()
print(1)
''', '''
y: int
z: int = call()
print(1)
''')

    source = '''
x: call() = 1
'''
    run_test(source, source)


def test_chained_and_unpacking_targets_are_kept():
    source = '''
a = b = 1
c, d = 1, 2
[e, f] = [1, 2]
'''
    run_test(source, source)


def test_attribute_and_subscript_targets_are_kept():
    source = '''
obj.x = 1
arr[0] = 99
'''
    run_test(source, source)


def test_augmented_assignment_is_a_use():
    source = '''
x = 0
x += 1
'''
    run_test(source, source)


def test_del_is_a_use():
    source = '''
x = 0
del x
'''
    run_test(source, source)


def test_loop_and_with_targets_are_kept():
    source = '''
for i in range(3):
    pass
with open('f') as fp:
    pass
'''
    run_test(source, source)


def test_dunder_names_are_kept():
    source = '''
__version__ = '1.0'
__author__ = 'me'
'''
    run_test(source, source)


def test_names_listed_in_all_are_kept():
    run_test('''
__all__ = ['x']
x = 1
y = 2
''', '''
__all__ = ['x']
x = 1
''')


def test_dynamic_all_keeps_every_module_variable():
    source = '''
__all__ = list_names()
x = 1
'''
    run_test(source, source)

    run_test('''
__all__ = list_names()
def f():
    y = 1
''', '''
__all__ = list_names()
def f():
    0
''')


def test_variable_used_in_nested_function():
    source = '''
x = 1
def f():
    return x
'''
    run_test(source, source)


def test_unused_variable_in_function():
    run_test('''
def f():
    x = 1
    return 2
''', '''
def f():
    return 2
''')


def test_function_variable_is_not_used_by_other_scopes():
    run_test('''
x = 1
def f():
    x = 2
    return 3
print(x)
''', '''
x = 1
def f():
    return 3
print(x)
''')

    run_test('''
x = 1
def f():
    x = 2
    return 3
''', '''
def f():
    return 3
''')


def test_variable_used_by_inner_function():
    source = '''
def f():
    x = 1
    def g():
        return x
    return g
'''
    run_test(source, source)


@pytest.mark.skipif(sys.version_info < (3, 0), reason='nonlocal needs python 3')
def test_nonlocal_declaration_is_a_use():
    source = '''
def f():
    x = 1
    def g():
        nonlocal x
        x = 2
    return g
'''
    run_test(source, source)


def test_global_declaration_is_a_use():
    source = '''
x = 1
def f():
    global x
    x = 2
'''
    run_test(source, source)


def test_class_attributes_are_kept():
    source = '''
class C:
    x = 1
'''
    run_test(source, source)


def test_variable_in_class_method():
    run_test('''
class C:
    def method(self):
        x = 1
        return 2
''', '''
class C:
    def method(self):
        return 2
''')


def test_variable_in_class_in_function_is_kept():
    source = '''
def f():
    class C:
        x = 1
    return C
'''
    run_test(source, source)


def test_empty_suite_is_replaced():
    run_test('''
def f():
    x = 1
''', '''
def f():
    0
''')

    run_test('''
if a:
    x = 1
else:
    y = 2
''', '''
if a:
    0
else:
    0
''')


def test_module_with_only_unused_variables_is_empty():
    run_test('''
a = 1
b = 2
''', '')


def test_removing_a_variable_can_make_another_unused():
    run_test('''
a = 1
b = a
c = b + 1
print(1)
''', 'print(1)')


def test_locals_taints_module():
    source = '''
def f():
    x = 1
    return locals()
'''
    run_test(source, source)


def test_star_import_taints_module():
    source = '''
from os import *
x = 1
'''
    run_test(source, source)
