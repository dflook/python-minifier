import os
import sys
import ast

from python_minifier import minify, unparse

def test_snippet():

    with open('snippet.py', 'rb') as f:
        source = f.read()

    try:
        original_ast = ast.parse(source)
    except SyntaxError:
        return

    # Test unparsing
    print('Unparsed:')
    print(unparse(original_ast))

    # Test transforms
    print('Transformed:')
    print(minify(source))

    print('Done')


if __name__ == '__main__':
    print('Interpreter version: ', sys.version_info)
    print('sys.path: ', sys.path)
    test_snippet()
