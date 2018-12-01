import os
import shutil
import sys
import ast
import pytest
import platform

from python_minifier import minify

import os

import json

try:
    import yaml
except ImportError:
    pass

def execute(python, path):
    from sh import Command
    python = Command(python)
    python(path)

class TestManifest(object):

    def __init__(self, python_version):
        self._python_version = python_version

        if python_version == 'python2.6':
            self._manifest_path = 'xtest/manifests/' + python_version + '_test_manifest.json'
        else:
            self._manifest_path = 'xtest/manifests/' + python_version + '_test_manifest.yaml'

        self._files = {}
        self.load()

        if python_version == 'pypy':
            self._base_path = '/usr/lib64/pypy-5.10/lib-python/2.7/test/'
        elif python_version == 'pypy3':
            self._base_path = '/usr/lib64/pypy3-5.10/lib-python/3/test/'
        else:
            self._base_path = os.path.join('/usr/lib64', python_version, 'test')

    @property
    def base_path(self):
        return self._base_path

    def load(self):
        if self._manifest_path.endswith('.json'):

            with open(self._manifest_path) as f:
                self._files = json.load(f)
        else:

            with open(self._manifest_path) as f:
                self._files = yaml.load(f)

    def all_runs(self):
        for path in sorted(self._files.keys()):
            info = self._files[path]

            if not info['ok']:
                continue

            if 'test_runs' not in info:
                self._files[path]['test_runs'] = []

            for options in [{}, {'rename_globals': True}, {'remove_literal_statements': True}, {'remove_literal_statements': True, 'rename_globals': True}]:
                run_info = self.get_run(path, options)

                if run_info is None:
                    continue

                if not run_info['ok']:
                    continue

                if 'skip' in run_info:
                    continue

                yield path, run_info

    def get_run(self, path, options):
        for run in self._files[path]['test_runs']:
            if run['options'] == options:
                return run

def get_manifest():
    if platform.python_implementation() == 'CPython':
        return TestManifest('python%i.%i' % (sys.version_info[0], sys.version_info[1]))
    else:
        if sys.version_info[0] == 2:
            return TestManifest('pypy')
        else:
            return TestManifest('pypy3')

manifest = get_manifest()

@pytest.mark.parametrize('test_run', manifest.all_runs())
def test_file(test_run):

    path, info = test_run

    options = info['options'].copy()
    if 'preserve_globals' in info:
        options['preserve_globals'] = info['preserve_globals']
    if 'preserve_locals' in info:
        options['preserve_locals'] = info['preserve_locals']
    if 'remove_annotations' in info:
        options['remove_annotations'] = info['remove_annotations']
    if 'hoist_literals' in info:
        options['hoist_literals'] = info['hoist_literals']

    try:
        with open(path, 'rb') as f:
            source = f.read()

        shutil.copy(path, path + '.bak')

        with open(path, 'wb') as f:
            f.write(minify(source, path, **options).encode())

        execute(sys.executable, path)
    finally:
        shutil.copy(path + '.bak', path)
