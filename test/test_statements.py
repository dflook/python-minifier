"""
Test statements correctly use parentheses when needed

The important things to test are expressions that might need parentheses:
- lambda
- named expressions
- tuples
  - empty
  - single element
  - multiple elements
- yield
- yield from
- attribute access

"""

import ast
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

@pytest.mark.parametrize('statement', [
    'a=1',
    'a=b=1',
    'a=1,',
    'a=b=1,',
    'a=1,2',
    'a=b=1,2',
    'a=()',
    'a=b=()',
    'a=*a',
    'a=*a,b',
    'a=b=*a',
    'a=*a,*c',
    'a=b=*a,*c',
    'a=lambda:1',
    'a=lambda a:1,',
    'a=1,lambda a:1',
    'a=*a,1,lambda a:1',
    'a=(b:=1)',
    'a=b=(c:=1)',
    'a=1 if True else 1',
    'a=b,1 if True else 1',
    'a=1 if True else 1,',
    'a=1 if True else 1,b',
    'a=yield',
    'a=yield 1',
    'a=yield from 1',
    'a=b.do',
    "a=''.join()"
])
def test_assign(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'a:int=1',
    'a:int=1,',
    'a:int=1,2',
    'a:int=()',
    'a:int=*a',
    'a:int=*a,b',
    'a:int=*a,*c',
    'a:int=lambda:1',
    'a:int=lambda a:1,',
    'a:int=1,lambda a:1',
    'a:int=*a,1,lambda a:1',
    'a:int=(b:=1)',
    'a:int=1 if True else 1',
    'a:int=b,1 if True else 1',
    'a:int=1 if True else 1,',
    'a:int=1 if True else 1,b',
    'a:int=yield',
    'a:int=yield 1',
    'a:int=yield from 1',
    'a:int=b.do',
    "a:int=''.join()"
])
def test_annassign(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'a+=1',
    'a+=1,',
    'a+=1,2',
    'a+=()',
    'a+=*a',
    'a+=*a,b',
    'a+=*a,*c',
    'a+=lambda:1',
    'a+=lambda a:1,',
    'a+=1,lambda a:1',
    'a+=*a,1,lambda a:1',
    'a+=(b:=1)',
    'a+=1 if True else 1',
    'a+=b,1 if True else 1',
    'a+=1 if True else 1,',
    'a+=1 if True else 1,b',
    'a+=yield',
    'a+=yield 1',
    'a+=yield from 1',
    'a+=b.do',
    "a+=''.join()"
])
def test_augassign(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    '1',
    '1,',
    '1,2',
    '()',
    '*a',
    '*a,b',
    '*a,*c',
    'lambda:1',
    'lambda a:1,',
    '1,lambda a:1',
    '*a,1,lambda a:1',
    'lambda:(a:=1)',
    'lambda:(yield)',
    'lambda:(yield a)',
    'lambda:(yield a,)',
    'lambda:(yield a,b)',
    'lambda:(yield(b:=1))',
    'lambda:(yield from a)',
    'lambda:(yield from(a,))',
    'lambda:(yield from(a,b))',
    '(b:=1)',
    '1 if True else 1',
    'b,1 if True else 1',
    '1 if True else 1,',
    '1 if True else 1,b',
    'yield',
    'yield 1',
    'yield from 1',
    'b.do',
    "''.join()"
])
def test_expression(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'assert 1',
    'assert 1,msg',
    'assert(1,2)',
    'assert(1,2),msg',
    'assert()',
    'assert(),msg',
    'assert lambda:1',
    'assert lambda a:1,msg',
    'assert(lambda:1,a),msg',
    'assert 1,lambda a:1',
    'assert(b:=1)',
    'assert 1 if True else 1',
    'assert(b,1 if True else 1),msg',
    'assert 1 if True else 1,msg',
    'assert(1 if True else 1,b)',
    'assert(yield)',
    'assert(yield 1)',
    'assert(yield from 1)',
    'assert b.do',
    "assert''.join()"
])
def test_assert(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'del a',
    ('del a,', 'del a'),
    'del a,b',
    'del()',
    'del b.do',
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
def test_del(statement):
    if isinstance(statement, tuple):
        statement, expected = statement
    else:
        expected = statement

    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == expected

@pytest.mark.parametrize('statement', [
    'return',
    'return 1',
    'return 1,',
    'return 1,2',
    'return()',
    'return*a',
    'return*a,b',
    'return*a',
    'return*a,*c',
    'return*a,*c',
    'return lambda:1',
    'return lambda a:1,',
    'return 1,lambda a:1',
    'return*a,1,lambda a:1',
    'return(b:=1)',
    'return 1 if True else 1',
    'return b,1 if True else 1',
    'return 1 if True else 1,',
    'return 1 if True else 1,b',
    'return b.do',
    "return''.join()"
])
def test_return(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'yield 1',
    'yield 1,',
    'yield 1,2',
    'yield()',
    'yield*a',
    'yield*a,b',
    'yield*a,*c',
    'yield lambda:1',
    'yield lambda a:1,',
    'yield 1,lambda a:1',
    'yield*a,1,lambda a:1',
    'yield(b:=1)',
    'yield 1 if True else 1',
    'yield b,1 if True else 1',
    'yield 1 if True else 1,',
    'yield 1 if True else 1,b',
    'yield from 1',
    'yield from(1,)',
    'yield from(1,2)',
    'yield b.do',
    "yield''.join()"
])
def test_yield(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'raise 1',
    'raise(1,)',
    'raise(1,2)',
    'raise()',
    'raise lambda:1',
    'raise(lambda a:1,)',
    'raise(1,lambda a:1)',
    'raise(*a,1,lambda a:1)',
    'raise(b:=1)',
    'raise 1 if True else 1',
    'raise(b,1 if True else 1)',
    'raise(1 if True else 1,)',
    'raise(1 if True else 1,b)',
    'raise b.do',
    "raise''.join()",
    'raise 1 from 1',
    'raise(1,)from(1,)',
    'raise(1,2)from(1,2)',
    'raise()from()',
    'raise lambda:1 from lambda:1',
    'raise(lambda a:1,)from(lambda a:1,)',
    'raise(1,lambda a:1)from(1,lambda a:1)',
    'raise(*a,1,lambda a:1)from(*a,1,lambda a:1)',
    'raise(b:=1)from(b:=1)',
    'raise 1 if True else 1 from 1 if True else 1',
    'raise(b,1 if True else 1)from(b,1 if True else 1)',
    'raise(1 if True else 1,)from(1 if True else 1,)',
    'raise(1 if True else 1,b)from(1 if True else 1,b)',
    'raise b.do from b.do',
    "raise''.join()from''.join()"
])
def test_raise(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'if 1:pass',
    'if(1,):pass',
    'if(1,2):pass',
    'if():pass',
    'if(*a,):pass',
    'if(*a,b):pass',
    'if(*a,*c):pass',
    'if lambda:1:pass',
    'if(lambda a:1,):pass',
    'if(1,lambda a:1):pass',
    'if(*a,1,lambda a:1):pass',
    'if b:=1:pass',
    'if 1 if True else 1:pass',
    'if(b,1 if True else 1):pass',
    'if(1 if True else 1,):pass',
    'if(1 if True else 1,b):pass',
    'if(yield):pass',
    'if(yield 1):pass',
    'if(yield from 1):pass',
    'if b.do:pass',
    "if''.join():pass"
])
def test_if(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'while 1:pass',
    'while(1,):pass',
    'while(1,2):pass',
    'while():pass',
    'while(*a,):pass',
    'while(*a,b):pass',
    'while(*a,*c):pass',
    'while lambda:1:pass',
    'while(lambda a:1,):pass',
    'while(1,lambda a:1):pass',
    'while(*a,1,lambda a:1):pass',
    'while b:=1:pass',
    'while 1 if True else 1:pass',
    'while(b,1 if True else 1):pass',
    'while(1 if True else 1,):pass',
    'while(1 if True else 1,b):pass',
    'while(yield):pass',
    'while(yield 1):pass',
    'while(yield from 1):pass',
    'while b.do:pass',
    "while''.join():pass"
])
def test_while(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'for a in a:pass',
    'for a,in a:pass',
    'for a,b in a:pass',
    'for()in a:pass',
    'for*a in a:pass',
    'for*a,b in a:pass',
    'for*a,*c in a:pass',
    'for b.do in a:pass',

    'for a in b:pass',
    'for a in b,:pass',
    'for a in b,c:pass',
    'for a in():pass',
    'for a in*a:pass',
    'for a in*a,b:pass',
    'for a in*a,*c:pass',
    'for a in lambda:1:pass',
    'for a in lambda a:1,:pass',
    'for a in 1,lambda a:1:pass',
    'for a in*a,1,lambda a:1:pass',
    'for a in(b:=1):pass',
    'for a in 1 if True else 1:pass',
    'for a in b,1 if True else 1:pass',
    'for a in 1 if True else 1,:pass',
    'for a in 1 if True else 1,b:pass',
    'for a in(yield):pass',
    'for a in(yield 1):pass',
    'for a in(yield from 1):pass',
    'for a in b.do:pass',
    "for a in''.join():pass"
])
def test_for(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    ' A',
    '(A,)',
    '(A,A)',
    '()',
    '*a',
    '(*a,b)',
    '(*a,*c)',
    ' lambda:A',
    '(lambda a:A,)',
    '(A,lambda a:A)',
    '(*a,A,lambda a:A)',
    '(b:=A)',
    ' A if True else A',
    '(b,A if True else A)',
    '(A if True else A,)',
    '(A if True else A,b)',
    '(yield)',
    '(yield A)',
    '(yield from A)',
    ' b.do',
    "''.join()"
])
def test_except(statement):

    statement = 'try:pass\nexcept' + statement + ':pass'

    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement