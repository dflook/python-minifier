from __future__ import print_function

import sys

import argparse
from pkg_resources import get_distribution, DistributionNotFound

from python_minifier import minify

try:
    version = get_distribution('python_minifier').version
except DistributionNotFound:
    version = '0.0.0'


def main():

    parser = argparse.ArgumentParser(prog='pyminify', description='Minify Python source')

    parser.add_argument('path', type=str, help='The source file to minify. Use "-" to read from stdin')

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

    parser.add_argument('-v', '--version', action='version', version=version)

    args = parser.parse_args()

    if args.path == '-':
        source = sys.stdin.read()
    else:
        with open(args.path, 'rb') as f:
            source = f.read()

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

    sys.stdout.write(
        minify(
            source,
            filename=args.path,
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
    )


if __name__ == '__main__':
    main()
