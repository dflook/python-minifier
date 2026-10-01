import ast

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.dead_code import eliminate_dead_code


def remove_unused_imports(source):
    module = ast.parse(source, 'remove_unused_imports')

    add_parent(module)
    add_namespace(module)
    return eliminate_dead_code(module, remove_imports=True, remove_variables=False, remove_definitions=False, remove_unreachable=False)


def run_test(source, expected):
    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_imports(source)
    compare_ast(expected_ast, actual_ast)


def test_unused_import():
    run_test('''
import os
print(1)
''', 'print(1)')


def test_used_import():
    source = '''
import os
print(os.getcwd())
'''
    run_test(source, source)


def test_unused_names_in_import():
    run_test('''
import os, sys, json
print(sys.argv)
''', '''
import sys
print(sys.argv)
''')


def test_unused_names_in_from_import():
    run_test('''
from os.path import join, exists, isdir
print(join('a', 'b'), exists('c'))
''', '''
from os.path import join, exists
print(join('a', 'b'), exists('c'))
''')


def test_unused_from_import_with_relative_module():
    run_test('''
from . import sibling
from .. import parent
print(parent)
''', '''
from .. import parent
print(parent)
''')


def test_unused_alias():
    run_test('''
import numpy as np
from os import path as p
print(1)
''', 'print(1)')


def test_used_alias_hides_original_name():
    source = '''
import numpy as np
from os import path as p
print(np, p)
'''
    run_test(source, source)


def test_original_name_of_alias_is_not_a_use():
    run_test('''
import numpy as np
print(numpy)
''', 'print(numpy)')


def test_dotted_import_binds_root_package():
    run_test('''
import os.path
print(1)
''', 'print(1)')

    source = '''
import os.path
print(os.sep)
'''
    run_test(source, source)


def test_dotted_imports_of_same_package_are_used_together():
    source = '''
import xml.dom
import xml.etree
print(xml.dom)
'''
    run_test(source, source)


def test_future_import_is_kept():
    source = '''
from __future__ import division
print(1)
'''
    run_test(source, source)


def test_import_used_in_function():
    source = '''
import os
def f():
    return os.getcwd()
'''
    run_test(source, source)


def test_import_used_in_class_body():
    source = '''
import os
class C:
    path = os.getcwd()
'''
    run_test(source, source)


def test_import_used_in_decorator_and_default():
    source = '''
import functools
import sys
@functools.lru_cache
def f(a=sys.maxsize):
    pass
'''
    run_test(source, source)


def test_unused_import_in_function():
    run_test('''
def f():
    import os
    return 1
''', '''
def f():
    return 1
''')


def test_function_import_is_not_used_by_other_scopes():
    run_test('''
import os
def f():
    import os
    return os.getcwd()
''', '''
def f():
    import os
    return os.getcwd()
''')


def test_import_in_class_body_is_kept():
    source = '''
class C:
    import os
'''
    run_test(source, source)


def test_empty_suite_is_replaced():
    run_test('''
def f():
    import os
''', '''
def f():
    0
''')

    run_test('''
try:
    import ujson
except ImportError:
    pass
''', '''
try:
    0
except ImportError:
    pass
''')


def test_module_with_only_unused_imports_is_empty():
    run_test('''
import os
from sys import argv
''', '')


def test_import_names_listed_in_all_are_kept():
    source = '''
import os
import sys
__all__ = ['os']
'''
    run_test(source, '''
import os
__all__ = ['os']
''')


def test_import_names_added_to_all_are_kept():
    run_test('''
import os
import sys
import json
__all__ = ['os']
__all__ += ['sys']
''', '''
import os
import sys
__all__ = ['os']
__all__ += ['sys']
''')


def test_dynamic_all_keeps_every_import():
    source = '''
import os
__all__ = sorted(['os'])
'''
    run_test(source, source)

    source = '''
import os
__all__ = []
__all__.append('os')
'''
    run_test(source, source)


def test_star_import_taints_module():
    source = '''
from os import *
import sys
'''
    run_test(source, source)


def test_exec_taints_module():
    source = '''
import sys
exec('print(sys)')
'''
    run_test(source, source)


def test_name_assigned_after_import_is_not_a_use():
    run_test('''
import os
os = None
''', '''
os = None
''')


def test_import_used_by_augmented_assignment_is_kept():
    source = '''
import os
os += 1
'''
    run_test(source, source)


def test_global_declaration_is_a_use():
    source = '''
import os
def f():
    global os
    os = None
'''
    run_test(source, source)
