import os
import sys

from test_file import test_file


def test_env():
    for sys_path in sys.path:
        for subdir, dirs, files in os.walk(sys_path):
            python_files = filter(lambda f: f.endswith('.py'), [os.path.join(subdir, file) for file in files])

            for path in python_files:
                test_file(path)

    print('Done')


if __name__ == '__main__':
    print('Interpreter version: ', sys.version_info)
    print('sys.path: ', sys.path)
    test_env()
