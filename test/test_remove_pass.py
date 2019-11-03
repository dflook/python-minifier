import ast
from python_minifier import add_namespace, bind_names, resolve_names
from python_minifier.transforms.remove_pass import RemovePass
from python_minifier.ast_compare import compare_ast

def remove_literals(source):
    module = ast.parse(source, 'remove_literals')

    add_namespace(module)
    bind_names(module)
    resolve_names(module)
    return RemovePass()(module)

def test_remove_pass_empty_module():
    source = 'pass'
    expected = ''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_pass_module():
    source = '''import collections
pass
a = 1
pass'''
    expected = '''import collections
a=1'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_if_empty():
    source = '''if True:
    pass'''
    expected = '''if True:
    0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_if_line():
    source = '''if True: pass'''
    expected = '''if True: 0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_suite():
    source = '''if True: 
    pass
    a=1 
    pass 
    return None'''
    expected = '''if True:
    a=1 
    return None'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_from_class():
    source = '''class A:
    pass
    a = 1
    pass
    def b():
        pass
        return 1
        pass
'''
    expected = '''class A:
    a=1
    def b():
        return 1
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_from_class_empty():
    source = '''class A:
    pass
'''
    expected = 'class A:0'

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_from_class_func_empty():
    source = '''class A:
    def b():
        pass
'''
    expected = '''class A:
    def b(): 0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source)
    compare_ast(expected_ast, actual_ast)
