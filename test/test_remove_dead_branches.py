import ast
import sys

import pytest

from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace, bind_names, resolve_names
from python_minifier.transforms.remove_dead_branches import RemoveDeadBranches


def parse(source):
    module = ast.parse(source, 'remove_dead_branches')

    add_parent(module)
    add_namespace(module)
    bind_names(module)
    resolve_names(module)
    return module


def remove_dead_branches(source):
    return RemoveDeadBranches()(parse(source))


def run_test(source, expected):
    expected_ast = ast.parse(expected)
    actual_ast = remove_dead_branches(source)
    compare_ast(expected_ast, actual_ast)


def skip_if_no_nameconstant():
    if sys.version_info < (3, 4):
        pytest.skip('NameConstant not in python < 3.4')


# region constant tests

def test_removes_false_branch():
    skip_if_no_nameconstant()
    run_test('''
if False:
    a()
else:
    b()
''', 'b()')


def test_removes_true_else_branch():
    skip_if_no_nameconstant()
    run_test('''
if True:
    a()
else:
    b()
''', 'a()')


def test_removes_bare_false_branch():
    skip_if_no_nameconstant()
    run_test('''
if False:
    a()
b()
''', 'b()')


def test_elif_chain_collapses():
    skip_if_no_nameconstant()
    run_test('''
if False:
    a()
elif False:
    b()
elif x:
    c()
else:
    d()
''', '''
if x:
    c()
else:
    d()
''')


def test_pads_empty_function():
    skip_if_no_nameconstant()
    run_test('''
def f():
    if False:
        a()
''', '''
def f():
    0
''')


def test_pads_empty_class():
    skip_if_no_nameconstant()
    run_test('''
class A:
    if False:
        a()
''', '''
class A:
    0
''')


def test_no_stray_padding_mid_suite():
    skip_if_no_nameconstant()
    run_test('''
def f():
    x = 1
    if False:
        a()
    return x
''', '''
def f():
    x = 1
    return x
''')


def test_pads_live_if_body():
    skip_if_no_nameconstant()
    run_test('''
if x:
    if False:
        a()
else:
    b()
''', '''
if x:
    0
else:
    b()
''')


def test_non_constant_test_kept():
    run_test('''
if x:
    a()
''', '''
if x:
    a()
''')


def test_none_test_kept():
    skip_if_no_nameconstant()
    run_test('''
if None:
    a()
''', '''
if None:
    a()
''')


def test_number_test_kept():
    run_test('''
if 0:
    a()
if 1:
    b()
''', '''
if 0:
    a()
if 1:
    b()
''')


def test_name_constants_kept_before_34():
    # On python 2 (and < 3.4) True and False are reassignable names
    if sys.version_info >= (3, 4):
        pytest.skip('True and False are NameConstant in python >= 3.4')

    run_test('''
if True:
    a()
if False:
    b()
''', '''
if True:
    a()
if False:
    b()
''')

# endregion

# region resolved_test marks

def test_resolved_test_false():
    module = parse('''
if x:
    a()
else:
    b()
''')
    module.body[0].resolved_test = False
    compare_ast(ast.parse('b()'), RemoveDeadBranches()(module))


def test_resolved_test_true():
    module = parse('''
if x:
    a()
else:
    b()
''')
    module.body[0].resolved_test = True
    compare_ast(ast.parse('a()'), RemoveDeadBranches()(module))


def test_resolved_test_overrides_constant():
    skip_if_no_nameconstant()

    module = parse('''
if True:
    a()
else:
    b()
''')
    module.body[0].resolved_test = False
    compare_ast(ast.parse('b()'), RemoveDeadBranches()(module))

# endregion

# region symbol table guards

def test_keeps_sole_local_binding():
    skip_if_no_nameconstant()
    source = '''
def f():
    if False:
        x = 1
    return x
'''
    run_test(source, source)


def test_removes_local_binding_bound_elsewhere():
    skip_if_no_nameconstant()
    run_test('''
def f():
    if False:
        x = 1
    x = 2
    return x
''', '''
def f():
    x = 2
    return x
''')


def test_keeps_generator_yield():
    skip_if_no_nameconstant()
    source = '''
def f():
    if False:
        yield
'''
    run_test(source, source)


def test_keeps_global_declaration():
    skip_if_no_nameconstant()
    source = '''
def f():
    if False:
        global x
    x = 1
'''
    run_test(source, source)


def test_keeps_nonlocal_declaration():
    skip_if_no_nameconstant()
    source = '''
def f():
    x = 1
    def g():
        if False:
            nonlocal x
            x = 2
'''
    run_test(source, source)


def test_nested_function_binding_does_not_mask():
    # g's local x must not count as a binding of x in f
    skip_if_no_nameconstant()
    source = '''
def f():
    if False:
        x = 1
    def g():
        x = 2
    return x
'''
    run_test(source, source)


def test_sibling_dead_branches_keep_one_binding():
    # Both branches can't be removed, or x would stop being a local.
    # The first branch found is removed greedily.
    skip_if_no_nameconstant()
    run_test('''
def f():
    if False:
        x = 1
    if False:
        x = 2
    return x
''', '''
def f():
    if False:
        x = 2
    return x
''')


def test_nested_dead_branches_keep_one_binding():
    # The dead branch inside the removed True branch is spliced into the
    # same suite, and must still count the condemned sibling binding
    skip_if_no_nameconstant()
    run_test('''
def f():
    if False:
        x = 1
    if True:
        if False:
            x = 2
    return x
''', '''
def f():
    if False:
        x = 2
    return x
''')


def test_keeps_namedexpr_in_comprehension():
    if sys.version_info < (3, 8):
        pytest.skip('NamedExpr not in python < 3.8')

    source = '''
def f():
    if False:
        [x for x in range(3) if (y := x)]
    return y
'''
    run_test(source, source)


def test_removes_when_namedexpr_bound_elsewhere():
    # The same NamedExpr binding also exists outside the dead branch, so removing
    # the branch does not change f's bindings and it can be removed.
    if sys.version_info < (3, 8):
        pytest.skip('NamedExpr not in python < 3.8')

    run_test('''
def f():
    if False:
        [x for x in range(3) if (y := x)]
    [x for x in range(3) if (y := x)]
    return y
''', '''
def f():
    [x for x in range(3) if (y := x)]
    return y
''')

# endregion

# region module and class namespaces

def test_removes_module_binding():
    skip_if_no_nameconstant()
    run_test('''
if False:
    DEBUG = True
print(1)
''', 'print(1)')


def test_removes_module_import():
    skip_if_no_nameconstant()
    run_test('''
if False:
    import logging
print(1)
''', 'print(1)')


def test_keeps_module_dead_nonlocal():
    # The original is a compile time SyntaxError, removing the branch shouldn't fix it
    skip_if_no_nameconstant()
    source = '''
if False:
    nonlocal x
'''
    run_test(source, source)


def test_keeps_module_dead_yield():
    # The original is a compile time SyntaxError, removing the branch shouldn't fix it
    skip_if_no_nameconstant()
    source = '''
if False:
    yield
'''
    run_test(source, source)


def test_removes_class_binding():
    # Class name resolution is dynamic when no function scope encloses the class
    skip_if_no_nameconstant()
    run_test('''
class C:
    if False:
        x = 1
    y = x
''', '''
class C:
    y = x
''')


def test_keeps_class_binding_in_function():
    # A binding in the class body stops loads deferring to the enclosing
    # function scope cell, so it can't be removed
    skip_if_no_nameconstant()
    source = '''
def f():
    x = 'cell'
    class C:
        if False:
            x = 1
        y = x
    return C.y
'''
    run_test(source, source)


def test_removes_class_branch_in_function_without_bindings():
    skip_if_no_nameconstant()
    run_test('''
def f():
    class C:
        if False:
            a()
        b()
''', '''
def f():
    class C:
        b()
''')


def test_keeps_class_global_declaration():
    # global in a class body applies to the whole class body
    skip_if_no_nameconstant()
    source = '''
class C:
    if False:
        global x
    x = 1
'''
    run_test(source, source)

# endregion

# region suite coverage

def test_removes_from_except_handler():
    skip_if_no_nameconstant()
    run_test('''
try:
    f()
except:
    if False:
        g()
    h()
''', '''
try:
    f()
except:
    h()
''')


def test_removes_from_finally():
    skip_if_no_nameconstant()
    run_test('''
try:
    f()
finally:
    if False:
        g()
    h()
''', '''
try:
    f()
finally:
    h()
''')


def test_removes_from_match_case():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    run_test('''
match x:
    case 1:
        if False:
            g()
        h()
''', '''
match x:
    case 1:
        h()
''')

# endregion

# region deep nesting

def stack_depth():
    depth = 0
    frame = sys._getframe()
    while frame is not None:
        depth += 1
        frame = frame.f_back
    return depth


def test_deep_elif_chain():
    # Machine generated dispatch code can contain elif chains hundreds of levels
    # deep. elif chains nest through the orelse suite without any indentation, so
    # they are not capped by the tokenizer's 100 level indentation limit and the
    # transform must not use more stack frames per level than other transforms.
    # The transform gets a fixed stack budget so the test doesn't depend on how
    # deep the test runner's own stack already is.
    source = 'if x0:\n a()\n' + ''.join('elif x%d:\n a()\n' % i for i in range(1, 150))

    limit = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(stack_depth() + 700)
        run_test(source, source)
    finally:
        sys.setrecursionlimit(limit)


def test_deep_constant_elif_chain():
    # A chain of dead elif branches is spliced level by level, which must not
    # exhaust the stack either
    skip_if_no_nameconstant()
    source = 'if False:\n a()\n' + ''.join('elif False:\n a()\n' for _ in range(1, 150))
    run_test(source, '')

# endregion

# region orelse cleanup

def test_drops_emptied_if_else():
    # A live if whose else is emptied by dead-branch removal drops the else
    # rather than keeping the 0 padding
    skip_if_no_nameconstant()
    run_test('''
if x:
    a()
else:
    if False:
        b()
''', '''
if x:
    a()
''')


def test_keeps_live_if_else():
    # The else still has a live statement, so it is kept
    skip_if_no_nameconstant()
    run_test('''
if x:
    a()
else:
    if False:
        b()
    c()
''', '''
if x:
    a()
else:
    c()
''')


def test_drops_user_written_else_zero():
    # A bare 0 expression else is a no-op, so it is dropped
    run_test('''
if x:
    a()
else:
    0
''', '''
if x:
    a()
''')


def test_keeps_padded_if_body():
    # The body of a live if is not optional, so its 0 padding is kept
    skip_if_no_nameconstant()
    run_test('''
if x:
    if False:
        a()
''', '''
if x:
    0
''')


def test_drops_emptied_while_else():
    skip_if_no_nameconstant()
    run_test('''
while x:
    a()
else:
    if False:
        b()
''', '''
while x:
    a()
''')


def test_drops_emptied_for_else():
    skip_if_no_nameconstant()
    run_test('''
for i in x:
    a()
else:
    if False:
        b()
''', '''
for i in x:
    a()
''')


def test_drops_emptied_try_else():
    skip_if_no_nameconstant()
    run_test('''
try:
    a()
except:
    b()
else:
    if False:
        c()
''', '''
try:
    a()
except:
    b()
''')


def test_keeps_padded_try_finally():
    # finally can't be dropped when there are no handlers, or try: would be bare
    skip_if_no_nameconstant()
    run_test('''
try:
    a()
finally:
    if False:
        c()
''', '''
try:
    a()
finally:
    0
''')

# endregion
