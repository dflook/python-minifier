import sys
from python_minifier import minify

sys.setrecursionlimit(20000)


def test_file(path):
    with open(path, 'rb') as f:
        try:
            return minify(f.read(), filename=path)
        except SyntaxError:
            pass

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: test_file.py <file>')
        exit(-1)

    print(test_file(sys.argv[1]))

    exit(0)
