import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_type_statement():
    if sys.version_info < (3, 12):
        pytest.skip('Improved generic syntax python < 3.12')


    source = '''
type Point = tuple[float, float]
type ListOrSet[T] = list[T] | set[T]
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_function_generic():
    if sys.version_info < (3, 12):
        pytest.skip('Improved generic syntax python < 3.12')

    source = '''
def a(): ...
def func[T](a: T, b: T) -> T:
    ...
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_class_generic():
    if sys.version_info < (3, 12):
        pytest.skip('Improved generic syntax python < 3.12')

    source = '''
class A:
    ...
class B[S]:
    ...
class C[T: str]:
    ...
'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))


def test_pep695_unparse():
    if sys.version_info < (3, 12):
        pytest.skip('Improved generic syntax python < 3.12')

    source = '''
class ClassA[T: str]:
    def method1(self) -> T:
        ...

def func[T](a: T, b: T) -> T:
    ...

type ListOrSet[T] = list[T] | set[T]

# This generic class is parameterized by a TypeVar T, a
# TypeVarTuple Ts, and a ParamSpec P.
class ChildClass[T, *Ts, **P]: ...

class ClassA[S, T](Protocol): ... # OK

class ClassB[S, T](Protocol[S, T]): ... # Recommended type checker error

class ClassA[T: str]: ...

class ClassA[T: dict[str, int]]: ...  # OK

class ClassB[T: "ForwardReference"]: ...  # OK

class ClassC[V]:
    class ClassD[T: dict[str, V]]: ...  # Type checker error: generic type

class ClassE[T: [str, int]]: ...  # Type checker error: illegal expression form

class ClassA[AnyStr: (str, bytes)]: ...  # OK

class ClassB[T: ("ForwardReference", bytes)]: ...  # OK

class ClassC[T: ()]: ...  # Type checker error: two or more types required

class ClassD[T: (str, )]: ...  # Type checker error: two or more types required

t1 = (bytes, str)
class ClassE[T: t1]: ...  # Type checker error: literal tuple expression required

class ClassF[T: (3, bytes)]: ...  # Type checker error: invalid expression form

class ClassG[T: (list[S], str)]: ...  # Type checker error: generic type

# A non-generic type alias
type IntOrStr = int | str

# A generic type alias
type ListOrSet[T] = list[T] | set[T]

# A type alias that includes a forward reference
type AnimalOrVegetable = Animal | "Vegetable"

# A generic self-referential type alias
type RecursiveList[T] = T | list[RecursiveList[T]]

T = TypeVar("T")
type MyList = list[T]  # Type checker error: traditional type variable usage

# The following generates no compiler error, but a type checker
# should generate an error because an upper bound type must be concrete,
# and ``Sequence[S]`` is generic. Future extensions to the type system may
# eliminate this limitation.
class ClassA[S, T: Sequence[S]]: ...

# The following generates no compiler error, because the bound for ``S``
# is lazily evaluated. However, type checkers should generate an error.
class ClassB[S: Sequence[T], T]: ...

class ClassA[T](BaseClass[T], param = Foo[T]): ...  # OK

print(T)  # Runtime error: 'T' is not defined

@dec(Foo[T])  # Runtime error: 'T' is not defined
class ClassA[T]: ...



def func1[T](a: T) -> T: ...  # OK

print(T)  # Runtime error: 'T' is not defined

def func2[T](a = list[T]): ...  # Runtime error: 'T' is not defined

@dec(list[T])  # Runtime error: 'T' is not defined
def func3[T](): ...

type Alias1[K, V] = Mapping[K, V] | Sequence[K]

S = 0

def outer1[S]():
    S = 1
    T = 1

    def outer2[T]():

        def inner1():
            nonlocal S  # OK because it binds variable S from outer1
            #nonlocal T  # Syntax error: nonlocal binding not allowed for type parameter

        def inner2():
            global S  # OK because it binds variable S from global scope

class Outer:
    class Private:
        pass

    # If the type parameter scope was like a traditional scope,
    # the base class 'Private' would not be accessible here.
    class Inner[T](Private, Sequence[T]):
        pass

    # Likewise, 'Inner' would not be available in these type annotations.
    def method1[T](self, a: Inner[T]) -> Inner[T]:
        return a

T = 0

@decorator(T)  # Argument expression `T` evaluates to 0
class ClassA[T](Sequence[T]):
    T = 1

    # All methods below should result in a type checker error
    # "type parameter 'T' already in use" because they are using the
    # type parameter 'T', which is already in use by the outer scope
    # 'ClassA'.
    def method1[T](self):
        ...

    def method2[T](self, x = T):  # Parameter 'x' gets default value of 1
        ...

    def method3[T](self, x: T):  # Parameter 'x' has type T (scoped to method3)
        ...

T = 0

# T refers to the global variable
print(T)  # Prints 0

class Outer[T]:
    T = 1

    # T refers to the local variable scoped to class 'Outer'
    print(T)  # Prints 1

    class Inner1:
        T = 2

        # T refers to the local type variable within 'Inner1'
        print(T)  # Prints 2

        def inner_method(self):
            # T refers to the type parameter scoped to class 'Outer';
            # If 'Outer' did not use the new type parameter syntax,
            # this would instead refer to the global variable 'T'
            print(T)  # Prints 'T'

    def outer_method(self):
        T = 3

        # T refers to the local variable within 'outer_method'
        print(T)  # Prints 3

        def inner_func():
            # T refers to the variable captured from 'outer_method'
            print(T)  # Prints 3

class ClassA[T1, T2, T3](list[T1]):
    def method1(self, a: T2) -> None:
        ...

    def method2(self) -> T3:
        ...

upper = ClassA[object, Dummy, Dummy]
lower = ClassA[T1, Dummy, Dummy]

upper = ClassA[Dummy, object, Dummy]
lower = ClassA[Dummy, T2, Dummy]

upper = ClassA[Dummy, Dummy, object]
lower = ClassA[Dummy, Dummy, T3]



T1 = TypeVar("T1", infer_variance=True)  # Inferred variance
T2 = TypeVar("T2")  # Invariant
T3 = TypeVar("T3", covariant=True)  # Covariant

# A type checker should infer the variance for T1 but use the
# specified variance for T2 and T3.
class ClassA(Generic[T1, T2, T3]): ...

K = TypeVar("K")

class ClassA[V](dict[K, V]): ...  # Type checker error

class ClassB[K, V](dict[K, V]): ...  # OK

class ClassC[V]:
    # The use of K and V for "method1" is OK because it uses the
    # "traditional" generic function mechanism where type parameters
    # are implicit. In this case V comes from an outer scope (ClassC)
    # and K is introduced implicitly as a type parameter for "method1".
    def method1(self, a: V, b: K) -> V | K: ...

    # The use of M and K are not allowed for "method2". A type checker
    # should generate an error in this case because this method uses the
    # new syntax for type parameters, and all type parameters associated
    # with the method must be explicitly declared. In this case, ``K``
    # is not declared by "method2", nor is it supplied by a new-style
    # type parameter defined in an outer scope.
    def method2[M](self, a: M, b: K) -> M | K: ...


'''

    expected_ast = ast.parse(source)
    unparse(expected_ast)

