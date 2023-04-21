import ast
import sys

import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast
from skip_invalid import skip_invalid


@pytest.mark.parametrize('statement', [
    '1 if 1 else 1',
    '1,2 if(1,2)else 1,2',
    '(1,)if(1,)else 1,',
    '()if()else()',
    'lambda:1 if(lambda:1)else lambda:1',
    '(lambda a:1,)if(lambda a:1,)else lambda a:1,',
    '1,lambda a:1 if(1,lambda a:1)else 1,lambda a:1',
    ('(a:=1)if(b:=1)else(b:=1)', sys.version_info >= (3, 8)),
    '(yield)if(yield)else(yield)',
    '(yield 1)if(yield 1)else(yield 1)',
    ('(yield from 1)if(yield from 1)else(yield from 1)', sys.version_info >= (3, 3)),
    'b.do if b.do else b.do',
    "''.join()if''.join()else''.join()",
    (('(a if b else a) if (a if b else a) else (a if b else a)', '(a if b else a)if(a if b else a)else a if b else a'), True)
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_if_exp(statement):
    if isinstance(statement, tuple):
        statement, expected = statement
    else:
        expected = statement

    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == expected

@pytest.mark.parametrize('statement', [
    '1+1',
    '1,2+1,2',
    '1,2+1,2',
    '1,+(1,)',
    '()+()',
    'lambda:1+(lambda:1)',
    'lambda:1,+(lambda:1,)',
    '1,lambda:1+1,lambda:1',
    ('(a:=1)+(b:=1)', sys.version_info >= (3, 8)),
    'yield+(yield)',
    'yield 1+(yield 1)',
    ('yield from 1+(yield from 1)', sys.version_info >= (3, 3)),
    'b.do+b.do',
    "''.join()+''.join()",
    'a if b else c+a if b else c'
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_binop(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'a()',
    '(1,2)()',
    '(1,)()',
    '()()',
    'lambda:1()',
    '(lambda a:1,)()',
    '(1,lambda a:1)()',
    ('(a:=1)()', sys.version_info >= (3, 8)),
    '(yield)()',
    '(yield 1)()',
    ('(yield from 1)()', sys.version_info >= (3, 3)),
    'b.do()',
    "''.join()()",
    '(a if b else a)()'
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_call(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    '1<1<1',
    '1,2<1,2<1,2',
    '(1,)<(1,)<1,',
    '()<()<()',
    '(lambda:1)<(lambda:1)<(lambda:1)',
    '(lambda a:1,)<(lambda a:1,)<(lambda a:1,)',
    '1,lambda a:1<1,lambda a:1<(1,lambda a:1)',
    ('(a:=1)<(b:=1)<(c:=1)', sys.version_info >= (3, 8)),
    '(yield)<(yield)<(yield)',
    '(yield 1)>(yield 1)>(yield 1)',
    ('(yield from 1)<(yield from 1)<(yield from 1)', sys.version_info >= (3, 3)),
    'b.do<b.do<b.do',
    "''.join()<''.join()<''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_compare(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    '(a for a in a)',
    '((a,)for a,in(a,))',
    '((a,b)for a,b in(a,b))',
    ('(()for()in())', sys.version_info >= (3, 0)),
    ('(1 for*a in 1)', sys.version_info >= (3, 0)),
    ('(1 for*a,b in 1)', sys.version_info >= (3, 0)),
    ('(1 for*a,*c in 1)', sys.version_info >= (3, 0)),
    '(b.do for b.do in b.do)',
    '(lambda:1 for a in(lambda:1))',
    '((lambda a:1,)for a in(lambda a:1,))',
    '((1,lambda a:1)for a in(1,lambda a:1))',
    ('(a:=1 for a in(a:=1))', sys.version_info >= (3, 8)),
    '((yield)for a in(yield))',
    '((yield 1)for a in(yield 1))',
    ('((yield from 1)for a in(yield from 1))', sys.version_info >= (3, 3)),
    "(''.join()for a in''.join())"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_comprehension(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    ('await 1', sys.version_info >= (3, 7)),
    ('await(1)', sys.version_info < (3, 7)),

    ('await 1,', sys.version_info >= (3, 7)),
    ('await(1)', sys.version_info < (3, 7)),

    ('await 1,2', sys.version_info >= (3, 7)),
    ('await(1,2)', sys.version_info < (3, 7)),

    'await()',
    'await(lambda:1)',

    ('await(lambda a:1,)', sys.version_info >= (3, 7)),
    ('await(lambda a:1)', sys.version_info < (3, 7)),

    'await(1,lambda a:1)',
    ('await(b:=1)', sys.version_info >= (3, 8)),

    ('await 1 if True else 1', sys.version_info >= (3, 7)),
    ('await(1 if True else 1)', sys.version_info < (3, 7)),

    ('await b,1 if True else 1', sys.version_info >= (3, 7)),
    ('await(b,1 if True else 1)', sys.version_info < (3, 7)),

    ('await 1 if True else 1,', sys.version_info >= (3, 7)),
    ('await(1 if True else 1)', sys.version_info < (3, 7)),

    ('await 1 if True else 1,b', sys.version_info >= (3, 7)),
    ('await(1 if True else 1,b)', sys.version_info < (3, 7)),

    ('await b.do', sys.version_info >= (3, 7)),
    ('await(b.do)', sys.version_info < (3, 7)),

    ("await''.join()", sys.version_info >= (3, 7)),
    ("await(''.join())", sys.version_info < (3, 7)),
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_await(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    '1,2',
    ('(a:=1,b:=32)', sys.version_info >= (3, 8)),
    ('(1,b:=32)', sys.version_info >= (3, 8)),
    'lambda:1,lambda:2',
    '1 if True else 1,2 if True else 2',
    '(a for a in a),(b for b in b)',
    'a or b,a and b',
    'a+b,a-b',
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_tuple(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'a[1]',
    ('a[a:=1]', sys.version_info >= (3, 8)),
    'a[lambda a:1]',
    'a[1 if True else 1]',
    'a[b.do]',
    "a[''.join()]",
    'a[1,2]',
    'a[1:1]',
    ('a[(a:=1):(b:=1)]', sys.version_info >= (3, 8)),
    'a[lambda:1:lambda:2]',
    'a[1 if True else 1:2 if True else 2]',
    'a[b.do:b.do]',
    "a[''.join():''.join()]",
    'a[1,2:1,2]',
    'a[1:1:1]',
    ('a[(a:=1):(b:=1):(c:=1)]', sys.version_info >= (3, 8)),
    'a[lambda:1:lambda:2:lambda:3]',
    'a[1 if True else 1:2 if True else 2:3 if True else 3]',
    'a[b.do:b.do:b.do]',
    "a[''.join():''.join():''.join()]",
    'a[1,2:1,2:1,2]',
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_slice(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    '{1:1}',
    '{(1,1):(1,1)}',
    '{(1,):(1,)}',
    '{():()}',
    ('{(a:=1):(a:=1)}', sys.version_info >= (3, 8)),
    '{lambda:1:lambda:1}',
    '{1 if True else 1:1 if True else 1}',
    '{b.do:b.do}',
    "{''.join():''.join()}",
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_dict(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    '{1}',
    '{1,1}',
    '{(1,)}',
    '{()}',
    ('{a:=1}', sys.version_info >= (3, 8)),
    '{lambda:1}',
    '{1 if True else 1}',
    '{b.do}',
    "{''.join()}",
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_set(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    '[1,1]',
    '[(1,1),(1,1)]',
    '[(1,),(1,)]',
    '[(),()]',
    ('[a:=1,b:=1]', sys.version_info >= (3, 8)),
    '[lambda:1,lambda:1]',
    '[1 if True else 1,1 if True else 1]',
    '[b.do,b.do]',
    "[''.join(),''.join()]",
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_list(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement
