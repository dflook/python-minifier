from __future__ import print_function

import sys
import os
from contextlib import contextmanager
import logging

import argparse
from pkg_resources import get_distribution, DistributionNotFound

from python_minifier import Minifier

try:
    version = get_distribution('python_minifier').version
except DistributionNotFound:
    version = '0.0.0'


logger = logging.getLogger(__name__)


def dash_none(s):
    if s == '-':
        return None
    return s


@contextmanager
def open_buffer(path=None, mode='r'):
    if mode not in ("r", "w"):
        raise ValueError("Unknown mode '{}', must be 'r' or 'w'".format(mode))
    if path is None:
        if mode == 'r':
            yield sys.stdin
        else:
            yield sys.stdout
    else:
        with open(path, mode) as f:
            yield f


def main():

    parser = argparse.ArgumentParser(prog='pyminify', description='Minify Python source')

    parser.add_argument('path', type=dash_none, help='The source file to minify. Use "-" to read from stdin')

    parser.add_argument(
        '--no-combine-imports',
        action='store_false',
        help='Disable combining adjacent import statements',
        dest='combine_imports',
    )
    parser.add_argument(
        '--no-remove-pass',
        action='store_false',
        default=True,
        help='Disable removing Pass statements',
        dest='remove_pass',
    )
    parser.add_argument(
        '--remove-literal-statements',
        action='store_true',
        help='Enable removing statements that are just a literal (including docstrings)',
        dest='remove_literal_statements',
    )
    parser.add_argument(
        '--no-remove-annotations',
        action='store_false',
        help='Disable removing function and variable annotations',
        dest='remove_annotations',
    )
    parser.add_argument(
        '--no-hoist-literals',
        action='store_false',
        help='Disable replacing string and bytes literals with variables',
        dest='hoist_literals',
    )
    parser.add_argument(
        '--no-rename-locals', action='store_false', help='Disable shortening of local names', dest='rename_locals'
    )
    parser.add_argument(
        '--preserve-locals',
        type=str,
        action='append',
        help='Comma separated list of local names that will not be shortened',
        dest='preserve_locals',
    )
    parser.add_argument(
        '--rename-globals', action='store_true', help='Enable shortening of global names', dest='rename_globals'
    )
    parser.add_argument(
        '--preserve-globals',
        type=str,
        action='append',
        help='Comma separated list of global names that will not be shortened',
        dest='preserve_globals',
    )
    parser.add_argument(
        '--no-remove-object-base',
        action='store_false',
        help='Disable removing object from base class list',
        dest='remove_object_base',
    )
    parser.add_argument(
        '--no-convert-posargs-to-args',
        action='store_false',
        help='Disable converting positional only arguments to normal arguments',
        dest='convert_posargs_to_args',
    )
    parser.add_argument(
        '--output',
        '-o',
        type=dash_none,
        help=(
            'Path to output file (if input is a file path or -), '
            'or directory (if input is a directory, '
            'in which case this argument is mandatory), or stdout if "-" (default).'
        ),
    )
    parser.add_argument(
        '--in-place',
        '-i',
        action='store_true',
        help='Replace file contents rather than writing to stdout.'
    )
    parser.add_argument(
        '--rec-copy-nonpy',
        '-n',
        action='store_true',
        help='If input is a directory, also copy non-"*.py" files into output directory.',
    )
    parser.add_argument(
        '--rec-delete-contents',
        '-d',
        action='store_true',
        help=(
            'If output is a non-empty directory, delete its contents. '
            'Ignored if input and output are the same.'
        ),
    )

    parser.add_argument('-v', '--version', action='version', version=version)

    args = parser.parse_args()

    preserve_globals = []
    if args.preserve_globals:
        for arg in args.preserve_globals:
            names = [name.strip() for name in arg.split(',') if name]
            preserve_globals.extend(names)

    preserve_locals = []
    if args.preserve_locals:
        for arg in args.preserve_locals:
            names = [name.strip() for name in arg.split(',') if name]
            preserve_locals.extend(names)

    minifier = Minifier(
        combine_imports=args.combine_imports,
        remove_pass=args.remove_pass,
        remove_annotations=args.remove_annotations,
        remove_literal_statements=args.remove_literal_statements,
        hoist_literals=args.hoist_literals,
        rename_locals=args.rename_locals,
        preserve_locals=preserve_locals,
        rename_globals=args.rename_globals,
        preserve_globals=preserve_globals,
        remove_object_base=args.remove_object_base,
        convert_posargs_to_args=args.convert_posargs_to_args,
    )

    if args.in_place:
        if args.output is not None:
            logger.warning('--in-place given; --output will be ignored')
        args.output = args.path

    if args.path and os.path.isdir(args.path):
        if args.output is None:
            raise ValueError('Input is a directory, but no --output directory given')
        minifier.minify_dir(
            os.path.abspath(args.path),
            os.path.abspath(args.output),
            args.rec_copy_nonpy,
            args.rec_delete_contents,
        )
    else:
        with open_buffer(args.path) as in_f:
            target = minifier.minify_buffer(in_f, args.path)

        with open_buffer(args.output) as out_f:
            out_f.write(target)


if __name__ == '__main__':
    main()
