import ast
import sys

import pytest

from python_minifier import minify, unparse
from python_minifier.ast_annotation import add_parent
from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace
from python_minifier.transforms.combine_imports import CombineImports


def combine_imports(module):
    add_parent(module)
    add_namespace(module)
    CombineImports()(module)
    return module


def imported_names(source):
    """
    The set of names imported by a module, with the laziness of the statement importing them

    Independent of how the import statements are grouped, so it is preserved by CombineImports.

    """

    names = set()

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add((None, 0, alias.name, alias.asname, node.is_lazy))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add((node.module, node.level, alias.name, alias.asname, node.is_lazy))

    return names


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    'statement', [
        'lazy import a',
        'lazy import a.b.c',
        'lazy import a as x',
        'lazy import a,b',
        'lazy import a as x,b as y',
        'lazy from x import y',
        'lazy from x import y,z',
        'lazy from x import y as z',
        'lazy from.x import y',
        'lazy from..x import y',
        'lazy from.import y'
    ]
)
def test_lazy_import_unparse(statement):
    """The lazy keyword is printed for lazy import statements"""
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    'statement', [
        'import a',
        'import a.b.c',
        'import a as x',
        'from x import y',
        'from x import*',
        'from.x import y'
    ]
)
def test_eager_import_unparse(statement):
    """The lazy keyword is not printed for regular import statements"""
    assert unparse(ast.parse(statement)) == statement


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    'source', [
        'def f():\n    lazy import a',
        'class C:\n    lazy import a',
        'if x:\n    lazy import a',
        'try:\n    lazy import a\nexcept ImportError:\n    pass',
        'async def f():\n    lazy from x import y'
    ]
)
def test_lazy_import_in_nested_scope(source):
    """Laziness survives a print/parse round trip wherever the statement appears"""
    expected_ast = ast.parse(source)
    actual_ast = ast.parse(unparse(ast.parse(source)))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_combine():
    source = '''lazy import builtins
lazy import collections'''
    expected = 'lazy import builtins, collections'

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_not_combined_with_eager():
    source = '''lazy import builtins
import collections'''
    expected = '''lazy import builtins
import collections'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_eager_import_not_combined_with_lazy():
    source = '''import builtins
lazy import collections'''
    expected = '''import builtins
lazy import collections'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_import_after_lazy_import_starts_new_group():
    """An import that can't join the current group starts the next one, rather than being left alone"""

    source = '''lazy import builtins
import collections
import functools'''
    expected = '''lazy import builtins
import collections, functools'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_alternating_lazy_and_eager_imports():
    source = '''import builtins
import collections
lazy import functools
lazy import datetime
import decimal'''
    expected = '''import builtins, collections
lazy import functools, datetime
import decimal'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_from_combine():
    source = '''lazy from builtins import dir
lazy from builtins import help'''
    expected = 'lazy from builtins import dir, help'

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_from_not_combined_with_eager():
    """Same module and level, but they must not merge because the laziness differs"""

    source = '''lazy from builtins import dir
from builtins import help'''
    expected = '''lazy from builtins import dir
from builtins import help'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_from_different_module_not_combined():
    source = '''lazy from builtins import dir
lazy from collections import abc'''
    expected = '''lazy from builtins import dir
lazy from collections import abc'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_from_relative_level_not_combined():
    source = '''lazy from .builtins import dir
lazy from ..builtins import help'''
    expected = '''lazy from .builtins import dir
lazy from ..builtins import help'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_star_not_combined():
    """A star import is never merged into a group, and never starts one"""

    source = '''lazy from breakfast import hashbrown
lazy from breakfast import *
lazy from breakfast import sausage
lazy from breakfast import bacon'''
    expected = '''lazy from breakfast import hashbrown
lazy from breakfast import *
lazy from breakfast import sausage, bacon'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_in_function():
    source = '''def test():
    lazy import collection as c
    lazy import builtins

    return None
'''
    expected = '''def test():
    lazy import collection as c, builtins
    return None
'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
def test_lazy_import_separated_by_statement():
    source = '''lazy import builtins
pass
lazy import collections'''
    expected = '''lazy import builtins
pass
lazy import collections'''

    expected_ast = ast.parse(expected)
    actual_ast = combine_imports(ast.parse(source))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    'source', [
        'lazy import a',
        'lazy import a\nlazy import b',
        'lazy import a\nimport b',
        'import a\nlazy import b\nimport c\nlazy import d',
        'lazy from x import y\nfrom x import z',
        'lazy from x import y\nlazy from x import z\nfrom x import w',
        'lazy import a as x\nlazy import b as y',
        'def f():\n    lazy import a\n    import b'
    ]
)
def test_minify_preserves_laziness(source):
    """Every name is still imported, with the same laziness, after a full minify"""
    assert imported_names(minify(source)) == imported_names(source)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    'source', [
        'lazy=1',
        'def lazy():pass',
        'class lazy:pass',
        'import lazy',
        'from lazy import x',
        'lazy=1\nlazy import a',
        'lazy import lazy'
    ]
)
def test_lazy_is_still_a_valid_identifier(source):
    """lazy is a soft keyword, so it remains usable as a name"""
    expected_ast = ast.parse(source)
    actual_ast = ast.parse(unparse(ast.parse(source)))
    compare_ast(expected_ast, actual_ast)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    ('source', 'expected'), [
        ('if x:\n    lazy import a\n    y=1', 'if x:lazy import a;y=1'),
        ('for i in r:\n    lazy import a\n    y=1', 'for i in r:lazy import a;y=1'),
        ('with c:\n    lazy import a\n    y=1', 'with c:lazy import a;y=1'),
        ('while x:\n    lazy import a\n    y=1', 'while x:lazy import a;y=1')
    ]
)
def test_lazy_import_joined_with_semicolon(source, expected):
    """A lazy import still parses when joined to the next statement with ';'"""
    assert minify(source) == expected


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    'source', [
        'lazy=1\nlazy import a',
        'lazy import a\nlazy=1',
        'lazy import lazy',
        'import a as lazy\nlazy import b',
        'def lazy():pass\nlazy import a'
    ]
)
def test_lazy_used_as_a_name_beside_a_lazy_import(source):
    """The soft keyword stays unambiguous when `lazy` is also an ordinary name"""
    assert imported_names(minify(source)) == imported_names(source)


@pytest.mark.skipif(sys.version_info < (3, 15), reason='Lazy imports require Python 3.15+')
@pytest.mark.parametrize(
    'source', [
        'if True:\n    lazy import a',
        'if False:\n    pass\nelse:\n    lazy import a'
    ]
)
def test_lazy_import_hoisted_out_of_a_dead_branch(source):
    """
    Removing a dead branch lifts a lazy import to module level, which is where
    PEP 810 requires it to be - it can never be moved into a function, class or
    try block, because it could not have been written there in the first place.
    """
    assert minify(source) == 'lazy import a'
