from __future__ import print_function

import sys

from python_minifier import minify


def main():
    if len(sys.argv) < 2:
        print('Usage: pyminify <PATH>')
        exit(-1)

    with open(sys.argv[1], 'rb') as f:
        print(minify(f.read()))


if __name__ == '__main__':
    main()
