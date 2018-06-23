import os

from test_file import test_file


def test_dir(path):
    for subdir, dirs, files in os.walk(path):
        python_files = filter(lambda f: f.endswith('.py'), [os.path.join(subdir, file) for file in files])

        for path in python_files:
            print(path)
            test_file(path)

    print('Done')


if __name__ == '__main__':
    test_dir('gh')
