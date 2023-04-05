import os
import sys
import ast
import pytest
import warnings
warnings.filterwarnings("ignore")

from python_minifier import minify, unparse

def gather_files():
    print('Interpreter version: ', sys.version_info)
    print('sys.path: ', sys.path)
    for sys_path in sys.path:
        for subdir, dirs, files in os.walk(sys_path):
            for file in filter(lambda f: f.endswith('.py'), [os.path.join(subdir, file) for file in files]):
                yield file

@pytest.mark.parametrize('path', gather_files())
def test_unparse(path):

    try:
        with open(path, 'rb') as f:
            source = f.read()
    except IOError:
        pytest.skip('IOError opening file')

    try:
        original_ast = ast.parse(source, path)
    except SyntaxError:
        pytest.skip('Invalid syntax in file')

    # Test unparsing
    unparse(original_ast)

    # Test transforms
    minify(source, filename=path)
