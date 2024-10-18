import ast
import sys

import pytest

from python_minifier import RemoveAnnotationsOptions
from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.remove_annotations import RemoveAnnotations


def remove_annotations(source, **kwargs):
    module = ast.parse(source)
    add_parent(module)
    add_namespace(module)
    RemoveAnnotations(RemoveAnnotationsOptions(**kwargs))(module)
    return module


def test_AnnAssign():

    if sys.version_info < (3, 6):
        pytest.skip('Variable annotation unsupported in python < 3.6')

    source = '''a :str = 1
b = 2
c : int = 3
def a(z: str) -> int: pass
class A:
    a: int
'''
    expected = '''a = 1
b = 2
c = 3
def a(z: str) -> int: pass
class A:
    a: int'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=True,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=False
    )
    compare_ast(expected_ast, actual_ast)


def test_FunctionDef():
    if sys.version_info < (3,):
        pytest.skip('Annotation unsupported in python < 3.0')

    # args and return are removed
    source = '''def test(a: str, b: int=1, *c: hello, **aws: crap) -> None:
    pass'''
    expected = '''def test(a, b=1, *c, **aws):
    pass'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=True,
        remove_argument_annotations=True,
        remove_class_attribute_annotations=False
    )
    compare_ast(expected_ast, actual_ast)

    # args only are removed
    source = '''def test(a: str, b: int=1, *c: hello, **aws: crap) -> None:
    pass'''
    expected = '''def test(a, b=1, *c, **aws) -> None:
    pass'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=False,
        remove_argument_annotations=True,
        remove_class_attribute_annotations=False
    )
    compare_ast(expected_ast, actual_ast)

    # return only are removed
    source = '''def test(a: str, b: int=1, *c: hello, **aws: crap) -> None:
    pass'''
    expected = '''def test(a: str, b: int=1, *c: hello, **aws: crap):
    pass'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=True,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=False
    )
    compare_ast(expected_ast, actual_ast)


def test_AsyncFunctionDef():
    if sys.version_info < (3, 6):
        pytest.skip('Async function unsupported in python < 3.5')

    source = '''async def test(a: str, b: int=1, *c: hello, **aws: crap) -> None:
    pass'''
    expected = '''async def test(a, b=1, *c, **aws):
    pass'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=True,
        remove_return_annotations=True,
        remove_argument_annotations=True,
        remove_class_attribute_annotations=False
    )
    compare_ast(expected_ast, actual_ast)


def test_AnnAssign_novalue():
    if sys.version_info < (3, 6):
        pytest.skip('Variable annotation unsupported in python < 3.6')

    source = '''a :str
class A:
    a: int
    def c(self, a: int) -> None: pass
'''
    expected = '''a:0
class A:
    a: int
    def c(self, a: int) -> None: pass
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=True,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=False
    )
    compare_ast(expected_ast, actual_ast)


def test_class_attributes():
    if sys.version_info < (3, 6):
        pytest.skip('Variable annotation unsupported in python < 3.6')

    source = '''a :str
class A:
    a: int
    b: int=2
    def c(self, a: int) -> None: pass
'''
    expected = '''a:str
class A:
    a:0
    b=2
    def c(self, a: int) -> None: pass
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=True
    )
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

@dataclasses.dataclass
class MyClass:
    myfield: int
    mysecondfile: str

@dataclass(frozen=True)
class MyClass:
    myfield: int
    mysecondfile: str

@dataclasses.dataclass(frozen=True)
class MyClass:
    myfield: int
    mysecondfile: str
'''
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=True
    )
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
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=True
    )
    compare_ast(expected_ast, actual_ast)


def test_no_remove_namedtuple():
    if sys.version_info < (3, 6):
        pytest.skip('annotations unavailable in python < 3.6')

    source = '''
class MyClass(NamedTuple):
    myfield: int
    mysecondfile: str

class MyClass2(typing.NamedTuple):
    myfield: int
    mysecondfile: str

class MyClass2(blah.NamedTuple):
    myfield: int
    mysecondfile: str
'''
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=True
    )
    compare_ast(expected_ast, actual_ast)


def test_remove():
    if sys.version_info < (3, 6):
        pytest.skip('annotations unavailable in python < 3.6')

    source = '''
class Dummy(NermedTupel):
    myfield: int
    mysecondfile: str

class Dummy(typing.NermedTupel):
    myfield: int
    mysecondfile: str
'''
    expected = '''
class Dummy(NermedTupel):
    myfield: 0
    mysecondfile: 0

class Dummy(typing.NermedTupel):
    myfield: 0
    mysecondfile: 0
'''
    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=True
    )
    compare_ast(expected_ast, actual_ast)


def test_no_remove_typeddict():
    if sys.version_info < (3, 8):
        pytest.skip('annotations unavailable in python < 3.6')

    source = '''
class Dummy(TypedDict):
    myfield: int
    mysecondfile: str

class Dummy(HypedDict):
    myfield: int
    mysecondfile: str

class Dummy(typing.TypedDict):
    myfield: int
    mysecondfile: str

class Dummy(typing.TypedDic):
    myfield: int
    mysecondfile: str
'''
    expected = '''
class Dummy(TypedDict):
    myfield: int
    mysecondfile: str

class Dummy(HypedDict):
    myfield: 0
    mysecondfile: 0

class Dummy(typing.TypedDict):
    myfield: int
    mysecondfile: str

class Dummy(typing.TypedDic):
    myfield: 0
    mysecondfile: 0

'''
    expected_ast = ast.parse(expected)
    actual_ast = remove_annotations(
        source,
        remove_variable_annotations=False,
        remove_return_annotations=False,
        remove_argument_annotations=False,
        remove_class_attribute_annotations=True
    )
    compare_ast(expected_ast, actual_ast)
