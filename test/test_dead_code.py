import ast
import sys

import pytest

from python_minifier import minify
from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.dead_code import eliminate_dead_code
from subprocess_compat import run_subprocess, safe_decode

SOURCE = '''
import os
import sys
import json

unused_variable = 42

def unused_function():
    return json.dumps({})

class UnusedClass:
    pass

def main():
    unused_local = 1
    return sys.argv
    print('unreachable')

call(main())
'''


def eliminate_all(source):
    module = ast.parse(source, 'dead_code')

    add_parent(module)
    add_namespace(module)
    return eliminate_dead_code(module, remove_imports=True, remove_variables=True, remove_definitions=True, remove_unreachable=True)


def run_test(source, expected):
    expected_ast = ast.parse(expected)
    actual_ast = eliminate_all(source)
    compare_ast(expected_ast, actual_ast)


def test_all_transforms_together():
    run_test(SOURCE, '''
import sys

def main():
    return sys.argv

call(main())
''')


def test_removing_a_function_makes_its_imports_unused():
    run_test('''
import json
def helper():
    return json.dumps({})
def main():
    return 1
print(main())
''', '''
def main():
    return 1
print(main())
''')


def test_removing_unreachable_code_makes_names_unused():
    run_test('''
import json
def helper():
    pass
def main():
    return 1
    return json.dumps(helper())
print(main())
''', '''
def main():
    return 1
print(main())
''')


def test_removing_a_variable_makes_its_import_unused():
    run_test('''
import json
value = json
print(1)
''', 'print(1)')


def test_values_with_side_effects_keep_their_imports():
    source = '''
from os.path import join
path = join('a', 'b')
print(1)
'''
    run_test(source, source)


def test_long_chain_of_dead_code():
    names = ['a%d' % i for i in range(20)]
    source = '\n'.join('def %s():\n    return %s()' % (name, following) for name, following in zip(names, names[1:]))
    source += '\ndef %s():\n    return 1\nprint(1)\n' % names[-1]
    run_test(source, 'print(1)')


def test_nothing_to_remove():
    source = '''
import sys
def main():
    return sys.argv
print(main())
'''
    run_test(source, source)


def test_tainted_module_is_not_changed():
    for source in ['from os import *\n' + SOURCE, SOURCE + "\neval('1')\n", 'import timeit\n' + SOURCE]:
        expected_ast = ast.parse(source)
        actual_ast = eliminate_all(source)
        compare_ast(expected_ast, actual_ast)


def test_options_are_disabled_by_default():
    assert minify(SOURCE) == minify(SOURCE, remove_unused_imports=False, remove_unused_variables=False, remove_unused_definitions=False, remove_unreachable=False)
    assert 'unused_function' in minify(SOURCE)
    assert 'unused_variable' in minify(SOURCE)
    assert 'UnusedClass' in minify(SOURCE)
    assert 'unreachable' in minify(SOURCE)
    assert 'import os' in minify(SOURCE)


def test_minify_options_are_independent():
    assert 'import os' not in minify(SOURCE, remove_unused_imports=True)
    assert 'unused_function' in minify(SOURCE, remove_unused_imports=True)

    assert 'unused_variable' not in minify(SOURCE, remove_unused_variables=True)
    assert 'import os' in minify(SOURCE, remove_unused_variables=True)

    assert 'unused_function' not in minify(SOURCE, remove_unused_definitions=True)
    assert 'UnusedClass' not in minify(SOURCE, remove_unused_definitions=True)
    assert 'unused_variable' in minify(SOURCE, remove_unused_definitions=True)

    assert 'unreachable' not in minify(SOURCE, remove_unreachable=True)
    assert 'unused_function' in minify(SOURCE, remove_unreachable=True)


def test_minify_removes_everything_dead():
    minified = minify(SOURCE, remove_unused_imports=True, remove_unused_variables=True, remove_unused_definitions=True, remove_unreachable=True)
    assert minified == 'import sys\ndef main():return sys.argv\ncall(main())'


def test_minify_with_renaming():
    minified = minify(SOURCE, remove_unused_imports=True, remove_unused_variables=True, remove_unused_definitions=True, remove_unreachable=True, rename_globals=True)
    assert minified == 'import sys\ndef A():return sys.argv\ncall(A())'


def test_minify_after_removing_asserts():
    source = '''
import os
def main():
    assert os
    return 1
print(main())
'''
    assert 'os' in minify(source, remove_unused_imports=True)
    assert 'os' not in minify(source, remove_asserts=True, remove_unused_imports=True)


@pytest.mark.skipif(sys.version_info < (3, 0), reason='annotations need python 3')
def test_minify_with_annotations():
    source = '''
import typing
def f(a: typing.List) -> None:
    pass
print(f)
'''
    assert 'typing' in minify(source, remove_annotations=False, remove_unused_imports=True)
    assert 'typing' not in minify(source, remove_unused_imports=True)


def test_minify_leaves_tainted_module_alone():
    source = 'from os import *\nimport sys\nx = 1\ncall(1)'
    assert minify(source, remove_unused_imports=True, remove_unused_variables=True, remove_unused_definitions=True, remove_unreachable=True) == 'from os import*\nimport sys\nx=1\ncall(1)'


def pyminify(*args):
    result = run_subprocess([sys.executable, '-m', 'python_minifier', '-'] + list(args), timeout=30, input_data=SOURCE)
    assert result.returncode == 0
    return safe_decode(result.stdout).replace('\r\n', '\n')


def test_cli_options_are_disabled_by_default():
    assert pyminify() == minify(SOURCE)


def test_cli_options():
    assert pyminify('--remove-unused-imports') == minify(SOURCE, remove_unused_imports=True)
    assert pyminify('--remove-unused-variables') == minify(SOURCE, remove_unused_variables=True)
    assert pyminify('--remove-unused-definitions') == minify(SOURCE, remove_unused_definitions=True)
    assert pyminify('--remove-unreachable') == minify(SOURCE, remove_unreachable=True)
