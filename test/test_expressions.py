import ast
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

@pytest.mark.parametrize('statement', [
    '1 if 1 else 1',
    '1,2 if(1,2)else 1,2',
    '(1,)if(1,)else 1,',
    '()if()else()',
    'lambda:1 if(lambda:1)else lambda:1',
    '(lambda a:1,)if(lambda a:1,)else lambda a:1,',
    '1,lambda a:1 if(1,lambda a:1)else 1,lambda a:1',
    '(a:=1)if(b:=1)else(b:=1)',
    '(yield)if(yield)else(yield)',
    '(yield 1)if(yield 1)else(yield 1)',
    '(yield from 1)if(yield from 1)else(yield from 1)',
    'b.do if b.do else b.do',
    "''.join()if''.join()else''.join()"
])
def test_if_exp(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    '1+1',
    '1,2+1,2',
    '1,2+1,2',
    '1,+(1,)',
    '()+()',
    'lambda:1+(lambda:1)',
    'lambda:1,+(lambda:1,)',
    '1,lambda:1+1,lambda:1',
    '(a:=1)+(b:=1)',
    'yield+(yield)',
    'yield 1+(yield 1)',
    'yield from 1+(yield from 1)',
    'b.do+b.do',
    "''.join()+''.join()"
])
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
    '(a:=1)()',
    '(yield)()',
    '(yield 1)()',
    '(yield from 1)()',
    'b.do()',
    "''.join()()"
])
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
    '(a:=1)<(b:=1)<(c:=1)',
    '(yield)<(yield)<(yield)',
    '(yield 1)>(yield 1)>(yield 1)',
    '(yield from 1)<(yield from 1)<(yield from 1)',
    'b.do<b.do<b.do',
    "''.join()<''.join()<''.join()"
])
def test_compare(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    '(a for a in a)',
    '((a,)for a,in(a,))',
    '((a,b)for a,b in(a,b))',
    '(()for()in())',
    '(1 for*a in 1)',
    '(1 for*a,b in 1)',
    '(1 for*a,*c in 1)',
    '(b.do for b.do in b.do)',
    '(lambda:1 for a in(lambda:1))',
    '((lambda a:1,)for a in(lambda a:1,))',
    '((1,lambda a:1)for a in(1,lambda a:1))',
    '(a:=1 for a in(a:=1))',
    '((yield)for a in(yield))',
    '((yield 1)for a in(yield 1))',
    '((yield from 1)for a in(yield from 1))',
    "(''.join()for a in''.join())"
])
def test_comprehension(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'await 1',
    'await 1,',
    'await 1,2',
    'await()',
    'await(lambda:1)',
    'await(lambda a:1,)',
    'await(1,lambda a:1)',
    'await(b:=1)',
    'await 1 if True else 1',
    'await b,1 if True else 1',
    'await 1 if True else 1,',
    'await 1 if True else 1,b',
    'await b.do',
    "await''.join()"
])
def test_await(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement
