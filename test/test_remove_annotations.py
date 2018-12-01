import ast
import sys
import pytest

from python_minifier import add_namespace
from python_minifier.transforms.remove_annotations import RemoveAnnotations
from python_minifier.ast_compare import compare_ast

def remove_annotations(source):
    module = ast.parse(source)
    add_namespace(module)
    RemoveAnnotations()(module)
    return module

def test_AnnAssign():

    if sys.version_info < (3, 6):
        pytest.skip('Variable annotation unsupported in python < 3.6')

    source = '''a :str = 1
b = 2
c : int = 3'''
    expected = '''a = 1
b = 2
c = 3'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(source)
    compare_ast(expected_ast, actual_ast)

def test_FunctionDef():
    if sys.version_info < (3,):
        pytest.skip('Annotation unsupported in python < 3.0')

    source = '''def test(a: str, b: int=1, *c: hello, **aws: crap) -> None:
    pass'''
    expected = '''def test(a, b=1, *c, **aws):
    pass'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(source)
    compare_ast(expected_ast, actual_ast)

def test_AsyncFunctionDef():
    if sys.version_info < (3, 6):
        pytest.skip('Async function unsupported in python < 3.5')

    source = '''async def test(a: str, b: int=1, *c: hello, **aws: crap) -> None:
    pass'''
    expected = '''async def test(a, b=1, *c, **aws):
    pass'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(source)
    compare_ast(expected_ast, actual_ast)

def test_AnnAssign_novalue():
    if sys.version_info < (3, 6):
        pytest.skip('Variable annotation unsupported in python < 3.6')

    source = '''a :str
'''
    expected = '''a:0'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(source)
    compare_ast(expected_ast, actual_ast)

def test_no_remove_dataclass():
    if sys.version_info < (3, 6):
        pytest.skip('annotations unavailable in python < 3.6')

    if sys.version_info < (3, 7):
        pytest.skip('dataclass unavailable in python < 3.7')

    source = '''
@dataclass
class MyClass:
    myfield: int
    mysecondfile: str
'''
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(source)
    compare_ast(expected_ast, actual_ast)

def test_remove_dataclass():
    if sys.version_info < (3, 6):
        pytest.skip('annotations unavailable in python < 3.6')

    if sys.version_info >= (3, 7):
        pytest.skip('dataclass available in python >= 3.7')

    source = '''
@dataclass
class MyClass:
    myfield: int
    mysecondfile: str
'''
    expected = '''
@dataclass
class MyClass:
    myfield: 0
    mysecondfile: 0
'''
    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(source)
    compare_ast(expected_ast, actual_ast)
