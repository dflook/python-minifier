import ast
import sys
import pytest
from python_minifier.transforms.hoist_literals import HoistLiterals
from python_minifier.ast_compare import AstComparer

if sys.version_info < (2, 7):
    pytestmark = pytest.mark.skip('No support on python 2.6')

def test_nohoist_single_usage():
    source = '''
a = 'Hello'
'''

    expected = '''
a = 'Hello'
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_hoist_multiple_usage():
    source = '''
A = 'Hello'
B = 'Hello'
'''

    expected = '''
C = 'Hello'
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_no_hoist_multiple_small():
    source = '''
A = '.'
B = '.'
'''

    expected = '''
A = '.'
B = '.'
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_hoist_multiple_small():
    source = '''
A = '.'
B = '.'
C = '.'
D = '.'
E = '.'
F = '.'
G = '.'
'''

    expected = '''
H = '.'
A = H
B = H
C = H
D = H
E = H
F = H
G = H
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_hoist_insert_after_docstring():
    source = '''
"Hello this is a docstring"
import collections
A = 'Hello'
B = 'Hello'
'''

    expected = '''
"Hello this is a docstring"
C = 'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)


def test_hoist_insert_after_future():
    source = '''
from  __future__ import print_function
import collections
A = 'Hello'
B = 'Hello'
'''

    expected = '''
from __future__ import print_function
C = 'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_hoist_insert_after_future_docstring():
    source = '''
"Hello this is a docstring"
from  __future__ import print_function
import collections
A = 'Hello'
B = 'Hello'
'''

    expected = '''
"Hello this is a docstring"
from __future__ import print_function
C = 'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_hoist_bytes():
    source = '''
"Hello this is a docstring"
from  __future__ import print_function
import collections
A = b'Hello'
B = b'Hello'
'''

    expected = '''
"Hello this is a docstring"
from __future__ import print_function
C = b'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_hoist_after_multiple_future():
    source = '''
"Hello this is a docstring"
from __future__ import print_function
from __future__ import sausages
import collections
A = b'Hello'
B = b'Hello'
'''

    expected = '''
"Hello this is a docstring"
from __future__ import print_function
from __future__ import sausages
C = b'Hello'
import collections
A = C
B = C
'''

    expected_ast = ast.parse(expected)
    actual_ast = HoistLiterals()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)
