import sys
import os.path
from setuptools import setup, find_packages

readme_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')
with open(readme_path) as f:
    long_desc = f.read()

install_requires = []
if sys.version_info < (2, 7):
    install_requires = ['argparse']

setup(
    name='python_minifier',
    description='Transform Python source code into it\'s most compact representation',
    author='Daniel Flook',
    author_email='daniel@flook.org',
    url='https://github.com/dflook/python-minifier',
    license='MIT',
    project_urls={
        'Issues': 'https://github.com/dflook/python-minifier/issues',
        'Documentation': 'https://dflook.github.io/python-minifier/',
    },
    keywords='minify minifier',

    use_scm_version=True,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    long_description=long_desc,
    long_description_content_type='text/markdown',

    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <3.10',
    setup_requires=['setuptools_scm'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'Topic :: Software Development'
    ],

    entry_points = {
        'console_scripts': ['pyminify=python_minifier.__main__:main']
    },

    install_requires=install_requires,

    zip_safe=True
)
