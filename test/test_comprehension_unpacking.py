"""
PEP 798 - unpacking in comprehensions, new in Python 3.15

    [*L for L in lists]      {*s for s in sets}
    (*L for L in lists)      {**d for d in dicts}

The dict form is represented as a DictComp whose `value` is None, with the
unpacked expression in `key`. The iterable forms reuse Starred in the existing
`elt` slot, so none of this changes any node's `_fields`.
"""

import ast
import sys

import pytest

from python_minifier import minify, unparse
from python_minifier.ast_compare import compare_ast


def run(source):
    """
    Execute a module and return the data it defines, for comparing behaviour

    Functions and classes are dropped: minifying renames them, and two function
    objects never compare equal anyway, so only the values they compute are
    useful for comparison.
    """

    namespace = {}
    exec(compile(source, '<test>', 'exec'), namespace)
    return {
        k: v for k, v in namespace.items()
        if not k.startswith('__') and not callable(v)
    }


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
@pytest.mark.parametrize(
    'statement', [
        'x=[*L for L in lists]',
        'x=[*L for L in lists if L]',
        'x=[*(a,b)for a in c]',
        'x={*s for s in sets}',
        'x=(*L for L in lists)',
        'x=[*L for L in lists for M in L]'
    ]
)
def test_iterable_comprehension_unpacking_unparse(statement):
    """The * form in list/set/generator comprehensions survives a print/parse round trip"""
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
@pytest.mark.parametrize(
    'statement', [
        'x={**d for d in dicts}',
        'x={**d for d in dicts if d}',
        "x={**{'a':1}for a in c}"
    ]
)
def test_dict_comprehension_unpacking_unparse(statement):
    """The ** form in dict comprehensions survives a print/parse round trip"""
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
@pytest.mark.parametrize(
    'statement', [
        'x=[*L for L in lists]',
        'x={*s for s in sets}',
        'x=(*L for L in lists)',
        'x={**d for d in dicts}'
    ]
)
def test_comprehension_unpacking_ast_preserved(statement):
    """Minifying does not change what the comprehension means"""
    expected_ast = ast.parse(statement)
    actual_ast = ast.parse(unparse(ast.parse(statement)))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
def test_iterable_unpacking_behaviour_is_preserved():
    source = '''
lists = [[1, 2], [3, 4], [5]]
sets = [{1, 2}, {2, 3}]
flat_list = [*L for L in lists]
flat_set = sorted({*s for s in sets})
flat_gen = list((*L for L in lists))
'''
    assert run(minify(source)) == run(source)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
def test_dict_unpacking_behaviour_is_preserved():
    source = '''
dicts = [{'a': 1}, {'b': 2}, {'a': 3}]
merged = {**d for d in dicts}
'''
    assert run(minify(source)) == run(source)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
def test_dict_unpacking_in_function_is_preserved():
    """Renaming must reach inside the unpacked expression of a dict comprehension"""
    source = '''
def merge(dictionaries):
    return {**dictionary for dictionary in dictionaries}
result = merge([{'a': 1}, {'b': 2}])
'''
    assert run(minify(source)) == run(source)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
def test_async_comprehension_unpacking():
    source = 'async def f(g):return(*a async for a in g())'
    assert unparse(ast.parse(source)) == source


# PEP 798 only allows the unpacking operator at the *top level of the element
# expression*, not nested inside a subexpression. How much of an expression the
# operator swallows differs by comprehension kind, because the grammar rules
# differ - listcomp/setcomp take `star_named_expression`, genexp takes
# `starred_expression`, dictcomp takes `double_starred_kvpair`:
#
#     [*x if c else z for x in y]     SyntaxError - needs parentheses
#     {*x if c else z for x in y}     SyntaxError - needs parentheses
#     (*x if c else z for x in y)     legal - binds the whole conditional
#     {**d if c else e for d in y}    legal - binds the whole conditional
#
# The restriction has nothing to do with which `for` clause is involved;
# multiple and nested comprehensions are unrestricted.

@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
@pytest.mark.parametrize(
    'source', [
        'q=[*x if c else z for x in y]',
        'q={*x if c else z for x in y}',
        'q=[**x for x in y]',
        'q=(**x for x in y)',
        'q={*k: v for k,v in y}'
    ]
)
def test_unpacking_restrictions_are_syntax_errors(source):
    """Forms PEP 798 does not allow, guarding the assumption the printer relies on"""
    with pytest.raises(SyntaxError):
        ast.parse(source)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
@pytest.mark.parametrize(
    ('source', 'expected'), [
        # the iterable forms need the parentheses kept, or the result will not parse
        ('q=[*(x if c else z) for x in y]', 'q=[*(x if c else z)for x in y]'),
        ('q={*(x if c else z) for x in y}', 'q={*(x if c else z)for x in y}'),
        # a tuple display element also needs its parentheses
        ('q=[(*x, *z) for x in y]', 'q=[(*x,*z)for x in y]'),
        # the dict form does not - the trailing `for` ends the expression
        ('q={**(d if c else e) for d in y}', 'q={**d if c else e for d in y}'),
        # the generator form does not require them either, but keeping them is
        # still correct, and it is the only iterable form where they are optional
        ('q=(*(x if c else z) for x in y)', 'q=(*(x if c else z)for x in y)')
    ]
)
def test_unpacking_parenthesisation(source, expected):
    """Parentheses are kept exactly where the grammar requires them, and dropped where it does not"""
    assert unparse(ast.parse(source)) == expected
    compare_ast(ast.parse(source), ast.parse(unparse(ast.parse(source))))


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Comprehension unpacking requires Python 3.15+')
@pytest.mark.parametrize(
    'source', [
        'q=[*x for x in y for z in x]',
        'q=[*x for x in y if x]',
        'q=[[*x for x in y] for z in w]',
        'q=[*[*x for x in y] for z in w]',
        'q=[*(x := y) for r in s]',
        'q=f(*x for x in y)',
        'q=[*x + z for x in y]',
        'q=[*(lambda: 1)() for x in y]',
        'q=(*x if c else z for x in y)'
    ]
)
def test_unpacking_in_compound_expressions(source):
    """Unpacking composes with multiple for clauses, nesting, walrus and calls"""
    compare_ast(ast.parse(source), ast.parse(unparse(ast.parse(source))))
