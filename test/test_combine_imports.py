import ast

from python_minifier import add_namespace
from python_minifier.transforms.combine_imports import CombineImports
from python_minifier.ast_compare import compare_ast

def combine_imports(module):
    add_namespace(module)
    CombineImports()(module)
    return module

def test_import():
    source = '''import builtins
import collections'''
    expected = 'import builtins, collections'


    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)

def test_import_as():
    source = '''import builtins
import collections as c
import functools as f
import datetime

pass'''
    expected = '''import builtins, collections as c, functools as f, datetime
pass'''


    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


def test_import_from():
    source = '''from builtins import dir
from builtins import help
import collections
from collections import abc'''
    expected = '''from builtins import dir, help 
import collections
from collections import abc'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)

def test_import_in_function():
    source = '''def test():
    import collection as c
    import builtins
    
    return None
'''
    expected = '''def test():
    import collection as c, builtins
    return None
'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


def test_import_star():
    source = '''
from breakfast import hashbrown
from breakfast import *
from breakfast import sausage
from breakfast import bacon
'''
    expected = '''
from breakfast import hashbrown
from breakfast import *
from breakfast import sausage, bacon
'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)
