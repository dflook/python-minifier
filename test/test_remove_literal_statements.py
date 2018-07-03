import ast
from python_minifier.transforms.remove_literal_statements import RemoveLiteralStatements
from python_minifier.ast_compare import AstComparer


def test_remove_literal_num():
    source = '213'
    expected = ''

    expected_ast = ast.parse(expected)
    actual_ast = RemoveLiteralStatements()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_remove_literal_str():
    source = '"hello"'
    expected = ''

    expected_ast = ast.parse(expected)
    actual_ast = RemoveLiteralStatements()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)

def test_complex():
    source = '''
"module docstring"
a = 'hello'

def t():
    "function docstring"
    a = 2
    0
    2
    'sadfsaf'
    def g():
        "just a docstring"

'''
    expected = '''
a = 'hello'
def t():
    a=2
    def g():
        0
'''

    expected_ast = ast.parse(expected)
    actual_ast = RemoveLiteralStatements()(ast.parse(source))
    AstComparer()(expected_ast, actual_ast)
