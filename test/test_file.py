import sys
import ast

from python_minifier import minify

sys.setrecursionlimit(20000)


def test_file(path):

    with open(path, 'rb') as f:
        source = f.read()

    try:
        ast.parse(source, path)
    except SyntaxError:
        return

    return minify(source, filename=path)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: test_file.py <file>')
        exit(-1)

    try:
        print(test_file(sys.argv[1]))
    except SyntaxError:
        print('Source file has a syntax error')
        raise

    exit(0)
