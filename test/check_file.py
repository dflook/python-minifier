import os
import sys
import ast

from python_minifier import minify, unparse

def test_env():

    with open('/usr/lib64/python3.7/test/ann_module.py', 'rb') as f:
        source = f.read()

    try:
        original_ast = ast.parse(source)
    except SyntaxError:
        return

    # Test unparsing
    unparse(original_ast)

    # Test transforms
    minify(source)

    print('Done')


if __name__ == '__main__':
    print('Interpreter version: ', sys.version_info)
    print('sys.path: ', sys.path)
    test_env()
