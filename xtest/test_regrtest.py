import os
import platform
import shutil
import sys

import pytest

from python_minifier import minify

try:
    import yaml
except ImportError:
    pass


class Manifest(object):
    """
    The test manifest for a python interpreter

    :param str interpreter: The python interpreter to use
    """

    def __init__(self, interpreter):
        self._interpreter = interpreter

        self._manifest_path = 'xtest/manifests/' + interpreter + '_test_manifest.yaml'

        self._files = {}
        self.load()

        if interpreter == 'pypy':
            self._base_path = '/usr/lib64/pypy-7.0/lib-python/2.7/test/'
        elif interpreter == 'pypy3':
            self._base_path = '/usr/lib64/pypy3-7.0/lib-python/3/test/'
        else:
            self._base_path = os.path.join('/usr/lib64', interpreter, 'test')

    def load(self):
        with open(self._manifest_path) as f:
            self._files = yaml.safe_load(f)

    def __len__(self):
        return sum([len(test_cases) for test_cases in self._files.values()])

    def __iter__(self):
        for path in sorted(self._files.keys()):
            for test_case in self._files[path]:
                yield Case(path, **test_case['options'])

    def verify(self):
        """
        Verify all test cases in the manifest pass
        """
        print('1..%i' % len(self))

        failed = 0

        for i, test_case in enumerate(self):
            try:
                test_case.run_test()
                print('ok %i - %s' % (i, test_case))
            except Exception as e:
                failed += 1
                print('not ok %i - %s' % (i, test_case))
                print(e)

        return failed

class Case(object):
    def __init__(self, test_path, **options):
        self.test_path = test_path
        self.options = options

    def __repr__(self):
        return 'Case(%r, **%r)' % (self.test_path, self.options)

    def __str__(self):
        return '%s with options %r' % (self.test_path, self.options)

    def run_test(self):
        from sh import Command, ErrorReturnCode

        ErrorReturnCode.truncate_cap = 1000

        def execute(python, path):
            python = Command(python)
            python(path)

        try:
            with open(self.test_path, 'rb') as f:
                source = f.read()

            shutil.copy(self.test_path, self.test_path + '.bak')

            with open(self.test_path, 'wb') as f:
                f.write(minify(source, self.test_path, **self.options).encode())

            execute(sys.executable, self.test_path)
        except ErrorReturnCode as e:
            print(self.test_path)
            print(e.stderr)
            raise
        finally:
            shutil.copy(self.test_path + '.bak', self.test_path)


def get_active_manifest():
    """
    The TestManifest for the current interpreter
    """

    if platform.python_implementation() == 'CPython':
        return Manifest('python%i.%i' % (sys.version_info[0], sys.version_info[1]))
    else:
        if sys.version_info[0] == 2:
            return Manifest('pypy')
        else:
            return Manifest('pypy3')


manifest = get_active_manifest()


@pytest.mark.parametrize('test_case', list(manifest), ids=lambda test_case: repr(test_case))
def test_regrtest(test_case):
    test_case.run_test()


if __name__ == '__main__':
    exit(manifest.verify())
