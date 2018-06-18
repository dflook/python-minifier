import sys
import os
from multiprocessing import Pool
from test_file import test_file


def test_env(concurrency=None):
    pool = Pool(concurrency)

    try:
        for sys_path in sys.path:
            for subdir, dirs, files in os.walk(sys_path):
                python_files = filter(lambda f: f.endswith('.py'), [os.path.join(subdir, file) for file in files])

                if concurrency == 1:
                    for path in python_files:
                        test_file(path)
                else:
                    pass
                    pool.map_async(test_file, python_files)

        print('All jobs submitted')
    finally:
        pool.close()
        pool.join()

    print('Done')


if __name__ == '__main__':
    print('Interpreter version: ', sys.version_info)
    print('sys.path: ', sys.path)
    test_env()
