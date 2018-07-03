import os
import sys
import ast

from python_minifier import minify, unparse

def test_env():

    for sys_path in sys.path:
        for subdir, dirs, files in os.walk(sys_path):
            python_files = filter(lambda f: f.endswith('.py'), [os.path.join(subdir, file) for file in files])

            for path in python_files:
                print(path)

                with open(path, 'rb') as f:
                    source = f.read()

                try:
                    original_ast = ast.parse(source, path)
                except SyntaxError:
                    continue

                # Test unparsing
                unparse(original_ast)

                # Test transforms
                minify(source, filename=path)

    print('Done')


if __name__ == '__main__':
    print('Interpreter version: ', sys.version_info)
    print('sys.path: ', sys.path)
    test_env()
