import ast

import pytest

from python_minifier import unparse


@pytest.mark.parametrize(
    'statement', [
        'import a',
        'import a,b',
        'import a as b',
        'import a as b,c as d',
        'import a.b',
        'import a.b.c',
        'import a.b.c as d',
        'import a.b.c as d,e as f',
        'from a import A',
        'from.import A',
        'from.import*',
        'from..import A,B',
        'from.a import A',
        'from...a import A',
        'from...a import*',
        'from a import A as B',
        'from a import A as B,C as D',
        'from.a.b import A',
        'from....a.b.c import A',
    ]
)
def test_import_statement(statement):
    assert unparse(ast.parse(statement)) == statement
