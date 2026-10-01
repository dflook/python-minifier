import ast
import sys

import pytest

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.dead_code import eliminate_dead_code


def remove_unused_definitions(source):
    module = ast.parse(source, 'remove_unused_definitions')

    add_parent(module)
    add_namespace(module)
    return eliminate_dead_code(module, remove_imports=False, remove_variables=False, remove_definitions=True, remove_unreachable=False)


def run_test(source, expected):
    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_definitions(source)
    compare_ast(expected_ast, actual_ast)


def test_unused_function():
    run_test('''
def unused():
    pass
print(1)
''', 'print(1)')


def test_unused_class():
    run_test('''
class Unused:
    pass
print(1)
''', 'print(1)')


@pytest.mark.skipif(sys.version_info < (3, 5), reason='async functions need python 3.5')
def test_unused_async_function():
    run_test('''
async def unused():
    pass
print(1)
''', 'print(1)')


def test_used_definitions():
    source = '''
def used():
    return 1
class Used:
    pass
print(used(), Used())
'''
    run_test(source, source)


def test_function_passed_as_argument_is_used():
    source = '''
def callback():
    pass
register(callback)
'''
    run_test(source, source)


def test_class_used_as_base_is_used():
    source = '''
class Base:
    pass
class Child(Base):
    pass
print(Child())
'''
    run_test(source, source)


def test_class_used_in_except_clause_is_used():
    source = '''
class MyError(Exception):
    pass
try:
    pass
except MyError:
    pass
'''
    run_test(source, source)


def test_decorated_definitions_are_kept():
    source = '''
@app.route('/')
def index():
    pass
@dataclass
class Config:
    pass
'''
    run_test(source, source)


def test_decorators_are_used():
    source = '''
def decorator(f):
    return f
@decorator
def main():
    pass
'''
    run_test(source, source)


def test_dunder_definitions_are_kept():
    source = '''
def __getattr__(name):
    pass
class __Meta__:
    pass
'''
    run_test(source, source)


def test_definitions_listed_in_all_are_kept():
    run_test('''
__all__ = ['helper', 'Helper']
def helper():
    pass
class Helper:
    pass
def other():
    pass
''', '''
__all__ = ['helper', 'Helper']
def helper():
    pass
class Helper:
    pass
''')


def test_dynamic_all_keeps_every_module_definition():
    source = '''
__all__ = names()
def helper():
    pass
'''
    run_test(source, source)


def test_methods_are_kept():
    source = '''
class C:
    def method(self):
        pass
    class Inner:
        pass
print(C)
'''
    run_test(source, source)


def test_unused_function_in_function():
    run_test('''
def outer():
    def inner():
        pass
    return 1
print(outer())
''', '''
def outer():
    return 1
print(outer())
''')


def test_used_function_in_function():
    source = '''
def outer():
    def inner():
        pass
    return inner
print(outer())
'''
    run_test(source, source)


def test_function_in_function_is_not_used_by_other_scopes():
    run_test('''
def helper():
    pass
def outer():
    def helper():
        pass
    return 1
print(helper(), outer())
''', '''
def helper():
    pass
def outer():
    return 1
print(helper(), outer())
''')


def test_empty_suite_is_replaced():
    run_test('''
def outer():
    def inner():
        pass
print(outer())
''', '''
def outer():
    0
print(outer())
''')


def test_definitions_that_evaluate_calls_are_kept():
    source = '''
def f(a=call()):
    pass
class C(base()):
    pass
class D:
    attribute = call()
class E:
    call()
'''
    run_test(source, source)


def test_definitions_with_harmless_defaults_are_removed():
    run_test('''
def f(a=1, *args, **kwargs):
    call()
class C(Base):
    x = 1
    y = 'text'
    def method(self, a=2):
        call()
    class Inner:
        pass
print(1)
''', 'print(1)')


@pytest.mark.skipif(sys.version_info < (3, 0), reason='keyword only arguments and metaclass keywords need python 3')
def test_definitions_with_harmless_keywords_are_removed():
    run_test('''
def f(a, *args, b=[], **kwargs):
    call()
class C(Base, metaclass=Meta):
    pass
print(1)
''', 'print(1)')


@pytest.mark.skipif(sys.version_info < (3, 0), reason='annotations need python 3')
def test_definitions_with_annotations_that_evaluate_calls_are_kept():
    source = '''
def f(a: call()):
    pass
def g() -> call():
    pass
'''
    run_test(source, source)

    run_test('''
def f(a: int, *args: str, b: 'text' = 1, **kwargs: dict) -> None:
    pass
print(1)
''', 'print(1)')


def test_removing_a_definition_can_make_another_unused():
    run_test('''
def a():
    return b()
def b():
    return c()
def c():
    return 1
print(1)
''', 'print(1)')


def test_exec_taints_module():
    source = '''
def f():
    pass
exec('f()')
'''
    run_test(source, source)
