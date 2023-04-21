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
import sys

import pytest

from python_minifier import unparse
from python_minifier.ast_compare import compare_ast
from skip_invalid import skip_invalid

@pytest.mark.parametrize('statement', [
    'a=1',
    'a=b=1',
    'a=1,',
    'a=b=1,',
    'a=1,2',
    'a=b=1,2',
    'a=()',
    'a=b=()',
    ('a=*a', sys.version_info >= (3, 0)),
    ('a=*a,b', sys.version_info >= (3, 0)),
    ('a=b=*a', sys.version_info >= (3, 0)),
    ('a=*a,*c', sys.version_info >= (3, 0)),
    ('a=b=*a,*c', sys.version_info >= (3, 0)),
    'a=lambda:1',
    'a=lambda a:1,',
    'a=1,lambda a:1',
    ('a=*a,1,lambda a:1', sys.version_info >= (3, 0)),
    ('a=(b:=1)', sys.version_info >= (3, 8)),
    ('a=b=(c:=1)', sys.version_info >= (3, 8)),
    'a=1 if True else 1',
    'a=b,1 if True else 1',
    'a=1 if True else 1,',
    'a=1 if True else 1,b',
    'a=yield',
    'a=yield 1',
    ('a=yield from 1', sys.version_info >= (3, 3)),
    'a=b.do',
    "a=''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_assign(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    'a:int=1',

    ('a:int=1,', sys.version_info >= (3, 8)),
    ('a:int=(1,)', sys.version_info < (3, 8)),

    ('a:int=1,2', sys.version_info >= (3, 8)),
    ('a:int=(1,2)', sys.version_info < (3, 8)),

    'a:int=()',

    ('a:int=*a', sys.version_info >= (3, 8)),
    ('a:int=(*a)', sys.version_info < (3, 8)),

    ('a:int=*a,b', sys.version_info >= (3, 8)),
    ('a:int=(*a,b)', sys.version_info < (3, 8)),

    ('a:int=*a,*c', sys.version_info >= (3, 8)),
    ('a:int=(*a,*c)', sys.version_info < (3, 8)),

    'a:int=lambda:1',

    ('a:int=lambda a:1,', sys.version_info >= (3, 8)),
    ('a:int=1,lambda a:1', sys.version_info >= (3, 8)),

    ('a:int=*a,1,lambda a:1', sys.version_info >= (3, 8)),
    ('a:int=(*a,1,lambda a:1)', sys.version_info < (3, 8)),

    ('a:int=(b:=1)', sys.version_info >= (3, 8)),

    'a:int=1 if True else 1',

    ('a:int=b,1 if True else 1', sys.version_info >= (3, 8)),
    ('a:int=(b,1 if True else 1)', sys.version_info < (3, 8)),

    ('a:int=1 if True else 1,', sys.version_info >= (3, 8)),
    ('a:int=(1 if True else 1,)', sys.version_info < (3, 8)),

    ('a:int=1 if True else 1,b', sys.version_info >= (3, 8)),
    ('a:int=(1 if True else 1,b)', sys.version_info < (3, 8)),

    ('a:int=yield', sys.version_info >= (3, 8)),
    ('a:int=(yield)', sys.version_info < (3, 8)),

    ('a:int=yield 1', sys.version_info >= (3, 8)),
    ('a:int=(yield 1)', sys.version_info < (3, 8)),

    ('a:int=yield from 1', sys.version_info >= (3, 8)),
    ('a:int=(yield from 1)', sys.version_info < (3, 8)),

    'a:int=b.do',
    "a:int=''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_annassign(statement):
    if sys.version_info < (3, 6):
        pytest.skip('annotations not supported')

    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    'a+=1',
    'a+=1,',
    'a+=1,2',
    'a+=()',
    ('a+=*a', sys.version_info >= (3, 9)),
    ('a+=*a,b', sys.version_info >= (3, 9)),
    ('a+=*a,*c', sys.version_info >= (3, 9)),
    ('a+=(*a)', (3, 0) < sys.version_info < (3, 9)),
    ('a+=(*a,b)', (3, 0) < sys.version_info < (3, 9)),
    ('a+=(*a,*c)', (3, 0) < sys.version_info < (3, 9)),
    'a+=lambda:1',
    'a+=lambda a:1,',
    'a+=1,lambda a:1',
    ('a+=*a,1,lambda a:1', sys.version_info >= (3, 9)),
    ('a+=(*a,1,lambda a:1)', (3, 0) <= sys.version_info < (3, 9)),
    ('a+=(b:=1)', sys.version_info >= (3, 8)),
    'a+=1 if True else 1',
    'a+=b,1 if True else 1',
    'a+=1 if True else 1,',
    'a+=1 if True else 1,b',
    'a+=yield',
    'a+=yield 1',
    ('a+=yield from 1', sys.version_info >= (3, 3)),
    'a+=b.do',
    "a+=''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
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
    ('*a', sys.version_info >= (3, 0)),
    ('*a,b', sys.version_info >= (3, 0)),
    ('*a,*c', sys.version_info >= (3, 0)),
    'lambda:1',
    'lambda a:1,',
    '1,lambda a:1',
    ('*a,1,lambda a:1', sys.version_info >= (3, 0)),
    ('lambda:(a:=1)', sys.version_info >= (3, 8)),
    'lambda:(yield)',
    'lambda:(yield a)',
    'lambda:(yield a,)',
    'lambda:(yield a,b)',
    ('lambda:(yield(b:=1))', sys.version_info >= (3, 8)),
    ('lambda:(yield from a)', sys.version_info >= (3, 3)),
    ('lambda:(yield from(a,))', sys.version_info >= (3, 3)),
    ('lambda:(yield from(a,b))', sys.version_info >= (3, 3)),
    ('(b:=1)', sys.version_info >= (3, 8)),
    '1 if True else 1',
    'b,1 if True else 1',
    '1 if True else 1,',
    '1 if True else 1,b',
    'yield',
    'yield 1',
    ('yield from 1', sys.version_info >= (3, 3)),
    'b.do',
    "''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_expression(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    'assert 1',
    'assert 1,msg',
    ('assert 1,(a:=1)', sys.version_info >= (3, 8)),
    'assert(1,2)',
    'assert(1,2),msg',
    'assert()',
    'assert(),msg',
    'assert lambda:1',
    'assert lambda a:1,msg',
    'assert(lambda:1,a),msg',
    'assert 1,lambda a:1',
    ('assert(b:=1)', sys.version_info >= (3, 8)),
    ('assert(b:=1),(c:=1)', sys.version_info >= (3, 8)),
    'assert 1 if True else 1',
    'assert(b,1 if True else 1),msg',
    'assert 1 if True else 1,msg',
    'assert(1 if True else 1,b)',
    'assert(yield)',
    'assert(yield 1)',
    ('assert(yield from 1)', sys.version_info >= (3, 3)),
    'assert b.do',
    "assert''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_assert(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    'del a',
    'del a,b',
    ('del()', sys.version_info >= (3, 0)),
    'del b.do',
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_del(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    'return',
    'return 1',
    'return 1,',
    'return 1,2',
    'return()',
    ('return*a', sys.version_info >= (3, 8)),
    ('return*a,b', sys.version_info >= (3, 8)),
    ('return*a', sys.version_info >= (3, 8)),
    ('return*a,*c', sys.version_info >= (3, 8)),
    ('return*a,*c', sys.version_info >= (3, 8)),
    ('return(*a)', (3, 0) < sys.version_info < (3, 8)),
    ('return(*a,b)', (3, 0) < sys.version_info < (3, 8)),
    ('return(*a)', (3, 0) < sys.version_info < (3, 8)),
    ('return(*a,*c)', (3, 0) < sys.version_info < (3, 8)),
    ('return(*a,*c)', (3, 0) < sys.version_info < (3, 8)),
    'return lambda:1',
    'return lambda a:1,',
    'return 1,lambda a:1',
    ('return*a,1,lambda a:1', sys.version_info >= (3, 8)),
    ('return(*a,1,lambda a:1)', (3, 0) < sys.version_info < (3, 8)),
    ('return(b:=1)', sys.version_info >= (3, 8)),
    'return 1 if True else 1',
    'return b,1 if True else 1',
    'return 1 if True else 1,',
    'return 1 if True else 1,b',
    'return b.do',
    "return''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
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
    ('yield*a', sys.version_info >= (3, 8)),
    ('yield*a,b', sys.version_info >= (3, 8)),
    ('yield*a,*c', sys.version_info >= (3, 8)),
    ('yield(*a)', (3, 0) < sys.version_info < (3, 8)),
    ('yield(*a,b)', (3, 0) < sys.version_info < (3, 8)),
    ('yield(*a,*c)', (3, 0) < sys.version_info < (3, 8)),
    'yield lambda:1',
    'yield lambda a:1,',
    'yield 1,lambda a:1',
    ('yield*a,1,lambda a:1', sys.version_info >= (3, 8)),
    ('yield(*a,1,lambda a:1)', (3, 0) < sys.version_info < (3, 8)),
    ('yield(b:=1)', sys.version_info >= (3, 8)),
    'yield 1 if True else 1',
    'yield b,1 if True else 1',
    'yield 1 if True else 1,',
    'yield 1 if True else 1,b',
    ('yield from 1', sys.version_info >= (3, 3)),
    ('yield from(1,)', sys.version_info >= (3, 3)),
    ('yield from(1,2)', sys.version_info >= (3, 3)),
    'yield b.do',
    "yield''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
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
    ('raise(*a,1,lambda a:1)', sys.version_info >= (3,0)),
    ('raise(b:=1)', sys.version_info >= (3,8)),
    'raise 1 if True else 1',
    'raise(b,1 if True else 1)',
    'raise(1 if True else 1,)',
    'raise(1 if True else 1,b)',
    'raise b.do',
    "raise''.join()",
    ('raise 1 from 1', sys.version_info >= (3, 0)),
    ('raise(1,)from(1,)', sys.version_info >= (3, 0)),
    ('raise(1,2)from(1,2)', sys.version_info >= (3, 0)),
    ('raise()from()', sys.version_info >= (3, 0)),
    ('raise lambda:1 from lambda:1', sys.version_info >= (3, 0)),
    ('raise(lambda a:1,)from(lambda a:1,)', sys.version_info >= (3, 0)),
    ('raise(1,lambda a:1)from(1,lambda a:1)', sys.version_info >= (3, 0)),
    ('raise(*a,1,lambda a:1)from(*a,1,lambda a:1)', sys.version_info >= (3, 0)),
    ('raise(b:=1)from(b:=1)', sys.version_info >= (3,8)),
    ('raise 1 if True else 1 from 1 if True else 1', sys.version_info >= (3, 0)),
    ('raise(b,1 if True else 1)from(b,1 if True else 1)', sys.version_info >= (3, 0)),
    ('raise(1 if True else 1,)from(1 if True else 1,)', sys.version_info >= (3, 0)),
    ('raise(1 if True else 1,b)from(1 if True else 1,b)', sys.version_info >= (3, 0)),
    ('raise b.do from b.do', sys.version_info >= (3, 0)),
    ("raise''.join()from''.join()" , sys.version_info >= (3, 0)),
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
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
    ('if(*a,):pass', sys.version_info > (3, 0)),
    ('if(*a,b):pass', sys.version_info > (3, 0)),
    ('if(*a,*c):pass', sys.version_info > (3, 0)),
    'if lambda:1:pass',
    'if(lambda a:1,):pass',
    'if(1,lambda a:1):pass',
    ('if(*a,1,lambda a:1):pass', sys.version_info > (3, 0)),
    ('if b:=1:pass', sys.version_info >= (3,8)),
    'if 1 if True else 1:pass',
    'if(b,1 if True else 1):pass',
    'if(1 if True else 1,):pass',
    'if(1 if True else 1,b):pass',
    'if(yield):pass',
    'if(yield 1):pass',
    ('if(yield from 1):pass', sys.version_info >= (3, 3)),
    'if b.do:pass',
    "if''.join():pass"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
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
    ('while(*a,):pass', sys.version_info >= (3, 0)),
    ('while(*a,b):pass', sys.version_info >= (3, 0)),
    ('while(*a,*c):pass', sys.version_info >= (3, 0)),
    'while lambda:1:pass',
    'while(lambda a:1,):pass',
    'while(1,lambda a:1):pass',
    ('while(*a,1,lambda a:1):pass', sys.version_info >= (3, 0)),
    ('while b:=1:pass', sys.version_info >= (3, 8)),
    'while 1 if True else 1:pass',
    'while(b,1 if True else 1):pass',
    'while(1 if True else 1,):pass',
    'while(1 if True else 1,b):pass',
    'while(yield):pass',
    'while(yield 1):pass',
    ('while(yield from 1):pass', sys.version_info >= (3, 3)),
    'while b.do:pass',
    "while''.join():pass"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_while(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement


@pytest.mark.parametrize('statement', [
    'for a in a:pass',
    'for a,in a:pass',
    'for a,b in a:pass',
    ('for()in a:pass', sys.version_info >= (3, 0)),
    ('for*a in a:pass', sys.version_info >= (3, 0)),
    ('for*a,b in a:pass', sys.version_info >= (3, 0)),
    ('for*a,*c in a:pass', sys.version_info >= (3, 0)),
    'for b.do in a:pass',
    'for a in b:pass',
    'for a in b,:pass',
    'for a in b,c:pass',
    'for a in():pass',
    ('for a in*a:pass', sys.version_info >= (3, 9)),
    ('for a in*a,b:pass', sys.version_info >= (3, 9)),
    ('for a in*a,*c:pass', sys.version_info >= (3, 9)),
    ('for a in(*a):pass', (3, 0) < sys.version_info < (3, 9)),
    ('for a in(*a,b):pass', (3, 0) < sys.version_info < (3, 9)),
    ('for a in(*a,*c):pass', (3, 0) < sys.version_info < (3, 9)),
    'for a in lambda:1:pass',
    'for a in lambda a:1,:pass',
    'for a in 1,lambda a:1:pass',
    ('for a in*a,1,lambda a:1:pass', sys.version_info >= (3, 9)),
    ('for a in(*a,1,lambda a:1):pass', (3, 0) < sys.version_info < (3, 9)),
    ('for a in(b:=1):pass', sys.version_info >= (3, 8)),
    'for a in 1 if True else 1:pass',
    'for a in b,1 if True else 1:pass',
    'for a in 1 if True else 1,:pass',
    'for a in 1 if True else 1,b:pass',
    'for a in(yield):pass',
    'for a in(yield 1):pass',
    ('for a in(yield from 1):pass', sys.version_info >= (3, 3)),
    'for a in b.do:pass',
    "for a in''.join():pass"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
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
    ('*a', sys.version_info >= (3, 11)),
    ('(*a,b)', sys.version_info > (3, 0)),
    ('(*a,*c)', sys.version_info > (3, 0)),
    ' lambda:A',
    '(lambda a:A,)',
    '(A,lambda a:A)',
    ('(*a,A,lambda a:A)', sys.version_info > (3, 0)),
    ('(b:=A)', sys.version_info >= (3, 8)),
    ' A if True else A',
    '(b,A if True else A)',
    '(A if True else A,)',
    '(A if True else A,b)',
    '(yield)',
    '(yield A)',
    ('(yield from A)', sys.version_info >= (3, 3)),
    ' b.do',
    "''.join()"
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_except(statement):

    statement = 'try:pass\nexcept' + statement + ':pass'

    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

@pytest.mark.parametrize('statement', [
    'with 1:pass',
    'with 1,2:pass',
    'with():pass',
    'with lambda:1:pass',
    'with 1,lambda a:1:pass',
    ('with(b:=1):pass', sys.version_info >= (3, 8)),
    'with 1 if True else 1:pass',
    'with b,1 if True else 1:pass',
    'with(yield):pass',
    'with(yield 1):pass',
    ('with(yield from 1):pass', sys.version_info >= (3, 3)),
    'with b.do:pass',
    "with''.join():pass",
    'with 1 as a:pass',
    'with 1,2 as a:pass',
    'with()as a:pass',
    'with lambda:1 as a:pass',
    'with 1,lambda a:1 as a,b:pass',
    ('with(b:=1)as a:pass', sys.version_info >= (3, 8)),
    'with 1 if True else 1 as a:pass',
    'with b,1 if True else 1 as a:pass',
    'with(yield)as a:pass',
    'with(yield 1)as a:pass',
    ('with(yield from 1)as a:pass', sys.version_info >= (3, 3)),
    'with b.do as a:pass',
    "with''.join()as a:pass",
], ids=lambda s: s[0] if isinstance(s, tuple) else s)
@skip_invalid
def test_with(statement):
    expected_ast = ast.parse(statement)
    minified = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(minified))
    assert minified == statement

