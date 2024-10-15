import ast
import sys

import pytest

from python_minifier import unparse
from python_minifier.ast_compare import compare_ast


@pytest.mark.parametrize(
    'statement', [
        'f"{1=!r:.4}"',
        'f"{1=:.4}"',
        'f"{1=!s:.4}"',
        'f"{1}"',
        'f"{1=}"',
        'f"{1=!s}"',
        'f"{1=!a}"'
    ]
)
def test_fstring_statement(statement):
    if sys.version_info < (3, 8):
        pytest.skip('f-string debug specifier added in python 3.8')

    assert unparse(ast.parse(statement)) == statement


def test_pep0701():
    if sys.version_info < (3, 12):
        pytest.skip('f-string syntax is bonkers before python 3.12')

    statement = 'f"{f"{f"{f"{"hello"}"}"}"}"'
    assert unparse(ast.parse(statement)) == statement

    statement = 'f"This is the playlist: {", ".join([])}"'
    assert unparse(ast.parse(statement)) == statement

    statement = 'f"{f"{f"{f"{f"{f"{1+1}"}"}"}"}"}"'
    assert unparse(ast.parse(statement)) == statement

    statement = '''
f"This is the playlist: {", ".join([
    'Take me back to Eden',  # My, my, those eyes like fire
    'Alkaline',              # Not acid nor alkaline
    'Ascensionism'           # Take to the broken skies at last
])}"
'''
    assert unparse(ast.parse(statement)) == 'f"This is the playlist: {", ".join(["Take me back to Eden","Alkaline","Ascensionism"])}"'

    # statement = '''print(f"This is the playlist: {"\N{BLACK HEART SUIT}".join(songs)}")'''
    # assert unparse(ast.parse(statement)) == statement

    statement = '''f"Magic wand: {bag["wand"]}"'''
    assert unparse(ast.parse(statement)) == statement

    statement = """
f'''A complex trick: {
 bag['bag']  # recursive bags!
}'''
    """
    assert unparse(ast.parse(statement)) == 'f"A complex trick: {bag["bag"]}"'

    statement = '''f"These are the things: {", ".join(things)}"'''
    assert unparse(ast.parse(statement)) == statement

    statement = '''f"{source.removesuffix(".py")}.c: $(srcdir)/{source}"'''
    assert unparse(ast.parse(statement)) == statement

    statement = '''f"{f"{f"infinite"}"}"+' '+f"{f"nesting!!!"}"'''
    assert unparse(ast.parse(statement)) == statement

    statement = '''f"{"\\n".join(a)}"'''
    assert unparse(ast.parse(statement)) == statement

    statement = '''f"{f"{f"{f"{f"{f"{1+1}"}"}"}"}"}"'''
    assert unparse(ast.parse(statement)) == statement

    statement = '''f"{"":*^{1:{1}}}"'''
    assert unparse(ast.parse(statement)) == statement

    # statement = '''f"{"":*^{1:{1:{1}}}}"'''
    # assert unparse(ast.parse(statement)) == statement
    # SyntaxError: f-string: expressions nested too deeply

    statement = '''f"___{
     x
}___"'''
    assert unparse(ast.parse(statement)) == '''f"___{x}___"'''

    statement = '''f"Useless use of lambdas: {(lambda x:x*2)}"'''
    assert unparse(ast.parse(statement)) == statement


def test_fstring_empty_str():
    if sys.version_info < (3, 6):
        pytest.skip('f-string expressions not allowed in python < 3.6')

    source = r'''
f"""\
{fg_br}"""
'''

    print(source)
    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))
