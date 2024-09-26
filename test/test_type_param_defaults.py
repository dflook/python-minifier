import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

# There are bizarrely few examples of this, some in the PEP are even syntax errors

def test_pep696():
    if sys.version_info < (3, 13):
        pytest.skip('Defaults for type parameters are not supported in python < 3.13')

    source = '''
type Alias[DefaultT = int, T] = tuple[DefaultT, T]  # SyntaxError: non-default TypeVars cannot follow ones with defaults

def generic_func[DefaultT = int, T](x: DefaultT, y: T) -> None: ...  # SyntaxError: non-default TypeVars cannot follow ones with defaults

class GenericClass[DefaultT = int, T]: ...  # SyntaxError: non-default TypeVars cannot follow ones with defaults

'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_pep696_2():
    if sys.version_info < (3, 13):
        pytest.skip('Defaults for type parameters are not supported in python < 3.13')

    source = '''
# TypeVars
class Foo[T = str]: ...

# ParamSpecs
class Baz[**P = [int, str]]: ...

# TypeVarTuples
class Qux[*Ts = *tuple[int, bool]]: ...

# TypeAliases
type Qux[*Ts = *tuple[str]] = Ham[*Ts]
type Rab[U, T = str] = Bar[T, U]
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_pep696_3():
    if sys.version_info < (3, 13):
        pytest.skip('Defaults for type parameters are not supported in python < 3.13')

    source = '''
class Foo[T = int]:
    def meth(self) -> Self:
        return self

reveal_type(Foo.meth)  # type is (self: Foo[int]) -> Foo[int]

'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_example():
    if sys.version_info < (3, 13):
        pytest.skip('Defaults for type parameters are not supported in python < 3.13')

    source = '''
def overly_generic[
   SimpleTypeVar,
   TypeVarWithDefault = int,
   TypeVarWithBound: int,
   TypeVarWithConstraints: (str, bytes),
   *SimpleTypeVarTuple = (int, float),
   **SimpleParamSpec = (str, bytearray),
](
   a: SimpleTypeVar,
   b: TypeVarWithDefault,
   c: TypeVarWithBound,
   d: Callable[SimpleParamSpec, TypeVarWithConstraints],
   *e: SimpleTypeVarTuple,
): ...
    '''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))