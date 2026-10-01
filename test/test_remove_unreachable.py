import ast
import sys

import pytest

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.dead_code import eliminate_dead_code


def remove_unreachable(source):
    module = ast.parse(source, 'remove_unreachable')

    add_parent(module)
    add_namespace(module)
    return eliminate_dead_code(module, remove_imports=False, remove_variables=False, remove_definitions=False, remove_unreachable=True)


def run_test(source, expected):
    expected_ast = ast.parse(expected)
    actual_ast = remove_unreachable(source)
    compare_ast(expected_ast, actual_ast)


def test_after_return():
    run_test('''
def f():
    return 1
    print('unreachable')
''', '''
def f():
    return 1
''')


def test_after_raise():
    run_test('''
def f():
    raise ValueError()
    print('unreachable')
''', '''
def f():
    raise ValueError()
''')


def test_after_break_and_continue():
    run_test('''
for i in range(10):
    if i:
        break
        print('unreachable')
    continue
    print('unreachable')
else:
    print('reachable')
print('reachable')
''', '''
for i in range(10):
    if i:
        break
    continue
else:
    print('reachable')
print('reachable')
''')


def test_removes_all_following_statements():
    run_test('''
def f():
    return 1
    x = 2
    def g():
        pass
    class C:
        pass
    print(x)
''', '''
def f():
    return 1
''')


def test_module_level():
    run_test('''
raise SystemExit(0)
print('unreachable')
''', 'raise SystemExit(0)')


def test_nested_suites():
    run_test('''
def f(a):
    while a:
        if a:
            return 1
            print('unreachable')
        for i in a:
            try:
                raise ValueError
                print('unreachable')
            except ValueError:
                continue
                print('unreachable')
            finally:
                pass
''', '''
def f(a):
    while a:
        if a:
            return 1
        for i in a:
            try:
                raise ValueError
            except ValueError:
                continue
            finally:
                pass
''')


def test_in_class_body():
    run_test('''
class C:
    raise ValueError
    x = 1
''', '''
class C:
    raise ValueError
''')


def test_if_else_that_both_terminate():
    run_test('''
def f(a):
    if a:
        return 1
    else:
        return 2
    print('unreachable')
''', '''
def f(a):
    if a:
        return 1
    else:
        return 2
''')

    run_test('''
def f(a, b):
    if a:
        return 1
    elif b:
        raise ValueError
    else:
        return 2
    print('unreachable')
''', '''
def f(a, b):
    if a:
        return 1
    elif b:
        raise ValueError
    else:
        return 2
''')


def test_if_that_may_not_terminate():
    source = '''
def f(a, b):
    if a:
        return 1
    print('reachable')
    if a:
        return 1
    else:
        pass
    print('reachable')
    if a:
        return 1
    elif b:
        return 2
    print('reachable')
'''
    run_test(source, source)


def test_try_with_handlers_that_all_terminate():
    run_test('''
def f():
    try:
        return 1
    except ValueError:
        return 2
    except KeyError:
        raise
    print('unreachable')
''', '''
def f():
    try:
        return 1
    except ValueError:
        return 2
    except KeyError:
        raise
''')


def test_try_that_may_not_terminate():
    source = '''
def f():
    try:
        return 1
    except ValueError:
        pass
    print('reachable')
    try:
        pass
    except ValueError:
        return 2
    print('reachable')
'''
    run_test(source, source)


def test_try_with_finally_that_terminates():
    run_test('''
def f():
    try:
        pass
    finally:
        return 1
    print('unreachable')
''', '''
def f():
    try:
        pass
    finally:
        return 1
''')


def test_try_with_finally_that_does_not_terminate():
    source = '''
def f():
    try:
        pass
    finally:
        cleanup()
    print('reachable')
'''
    run_test(source, source)


def test_try_body_that_terminates_with_finally():
    run_test('''
def f():
    try:
        return 1
    finally:
        cleanup()
    print('unreachable')
''', '''
def f():
    try:
        return 1
    finally:
        cleanup()
''')


def test_try_else_that_terminates():
    run_test('''
def f():
    try:
        pass
    except ValueError:
        return 1
    else:
        return 2
    print('unreachable')
''', '''
def f():
    try:
        pass
    except ValueError:
        return 1
    else:
        return 2
''')


def test_with_that_returns():
    run_test('''
def f():
    with open('f') as fp:
        return fp.read()
    print('unreachable')
''', '''
def f():
    with open('f') as fp:
        return fp.read()
''')


def test_with_that_raises_may_suppress_the_exception():
    source = '''
def f():
    with suppress(ValueError):
        raise ValueError
    print('reachable')
    with suppress(ValueError):
        if a:
            return 1
        else:
            raise ValueError
    print('reachable')
'''
    run_test(source, source)


def test_loops_may_not_terminate():
    source = '''
def f(a):
    for i in a:
        return 1
    print('reachable')
    while a:
        return 1
    print('reachable')
    while True:
        return 1
    print('reachable')
'''
    run_test(source, source)


@pytest.mark.skipif(sys.version_info < (3, 10), reason='match needs python 3.10')
def test_match_may_not_terminate():
    source = '''
def f(a):
    match a:
        case 1:
            return 1
        case _:
            return 2
    print('reachable')
'''
    run_test(source, source)


def test_yield_is_kept():
    source = '''
def f():
    return
    yield
'''
    run_test(source, source)

    source = '''
def f():
    return
    x = yield
'''
    run_test(source, source)


def test_yield_in_nested_function_is_removed():
    run_test('''
def f():
    return
    def g():
        yield
''', '''
def f():
    return
''')


@pytest.mark.skipif(sys.version_info < (3, 3), reason='yield from needs python 3.3')
def test_yield_from_is_kept():
    source = '''
def f():
    return
    yield from g()
'''
    run_test(source, source)


def test_global_declaration_is_kept():
    source = '''
def f():
    return
    global x
    x = 1
'''
    run_test(source, source)


@pytest.mark.skipif(sys.version_info < (3, 0), reason='nonlocal needs python 3')
def test_nonlocal_declaration_is_kept():
    source = '''
def f():
    x = 1
    def g():
        return
        nonlocal x
    return g
'''
    run_test(source, source)


def test_only_assignment_to_a_local_name_is_kept():
    source = '''
x = 1
def f():
    return x
    x = 2
'''
    run_test(source, source)

    source = '''
x = 1
def f():
    return x
    def x():
        pass
'''
    run_test(source, source)

    source = '''
x = 1
def f():
    return x
    import x
'''
    run_test(source, source)

    source = '''
x = 1
def f():
    def g():
        return x
    return g
    x = 2
'''
    run_test(source, source)


def test_local_name_that_is_not_used_otherwise_is_removed():
    run_test('''
def f():
    return 1
    x = 2
    print(x)
''', '''
def f():
    return 1
''')


def test_local_name_that_is_still_bound_is_removed():
    run_test('''
def f():
    x = 1
    return x
    x = 2
''', '''
def f():
    x = 1
    return x
''')


def test_module_names_are_dynamic():
    run_test('''
print(x)
raise SystemExit
x = 1
''', '''
print(x)
raise SystemExit
''')


def test_class_names_are_dynamic():
    run_test('''
class C:
    print(x)
    raise ValueError
    x = 1
''', '''
class C:
    print(x)
    raise ValueError
''')


def test_class_names_in_function_are_kept():
    source = '''
def f():
    x = 1
    class C:
        print(x)
        raise ValueError
        x = 2
    return C
'''
    run_test(source, source)


def test_exec_taints_module():
    source = '''
def f():
    return 1
    print('unreachable')
exec('f()')
'''
    run_test(source, source)
