from __future__ import print_function

import sys
import os

import argparse
from pkg_resources import get_distribution, DistributionNotFound

from python_minifier import minify

try:
    version = get_distribution('python_minifier').version
except DistributionNotFound:
    version = '0.0.0'


def main():
    """
examples:
  # Minifying stdin to stdout
  pyminify -

  # Minifying a file to stdout
  pyminify example.py

  # Minifying a file and writing to a different file
  pyminify example.py --output example.min.py

  # Minifying a file in place
  pyminify example.py --in-place

  # Minifying all *.py files in a directory
  pyminify src/ --in-place

  # Minifying multiple paths in place
  pyminify file1.py file2.py src/ --in-place
"""

    args = parse_args()

    if len(args.path) == 1 and args.path[0] == '-':
        # minify stdin
        source = sys.stdin.buffer.read() if sys.version_info >= (3, 0) else sys.stdin.read()
        minified = do_minify(source, 'stdin', args)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(minified)
        else:
            sys.stdout.write(minified)

    else:
        # minify source paths
        for path in source_modules(args):
            if args.output or args.in_place:
                sys.stdout.write(path + '\n')

            with open(path, 'rb') as f:
                source = f.read()

            minified = do_minify(source, path, args)

            if args.in_place:
                with open(path, 'w') as f:
                    f.write(minified)
            elif args.output:
                with open(args.output, 'w') as f:
                    f.write(minified)
            else:
                sys.stdout.write(minified)

def parse_args():
    parser = argparse.ArgumentParser(prog='pyminify', description='Minify Python source code', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=main.__doc__)

    parser.add_argument(
        'path',
        nargs='+',
        type=str,
        help='The source file or directory to minify. Use "-" to read from stdin. Directories are recursively searched for ".py" files to minify. May be used multiple times',
    )

    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument(
        '--output', '-o',
        action='store',
        help='Path to write minified output. Can only be used when the source is a single module. Outputs to stdout by default',
        dest='output'
    )
    output_options.add_argument(
        '--in-place', '-i',
        action='store_true',
        help='Overwrite existing files. Required when there is more than one source module',
        dest='in_place'
    )

    # Minification arguments
    minification_options = parser.add_argument_group('minification options', 'Options that affect how the source is minified')
    minification_options.add_argument(
        '--no-combine-imports',
        action='store_false',
        help='Disable combining adjacent import statements',
        dest='combine_imports',
    )
    minification_options.add_argument(
        '--no-remove-pass',
        action='store_false',
        default=True,
        help='Disable removing Pass statements',
        dest='remove_pass',
    )
    minification_options.add_argument(
        '--remove-literal-statements',
        action='store_true',
        help='Enable removing statements that are just a literal (including docstrings)',
        dest='remove_literal_statements',
    )
    minification_options.add_argument(
        '--no-remove-annotations',
        action='store_false',
        help='Disable removing function and variable annotations',
        dest='remove_annotations',
    )
    minification_options.add_argument(
        '--no-hoist-literals',
        action='store_false',
        help='Disable replacing string and bytes literals with variables',
        dest='hoist_literals',
    )
    minification_options.add_argument(
        '--no-rename-locals',
        action='store_false',
        help='Disable shortening of local names',
        dest='rename_locals'
    )
    minification_options.add_argument(
        '--preserve-locals',
        type=str,
        action='append',
        help='Comma separated list of local names that will not be shortened',
        dest='preserve_locals',
        metavar='LOCAL_NAMES'
    )
    minification_options.add_argument(
        '--rename-globals',
        action='store_true',
        help='Enable shortening of global names',
        dest='rename_globals'
    )
    minification_options.add_argument(
        '--preserve-globals',
        type=str,
        action='append',
        help='Comma separated list of global names that will not be shortened',
        dest='preserve_globals',
        metavar='GLOBAL_NAMES'
    )
    minification_options.add_argument(
        '--no-remove-object-base',
        action='store_false',
        help='Disable removing object from base class list',
        dest='remove_object_base',
    )
    minification_options.add_argument(
        '--no-convert-posargs-to-args',
        action='store_false',
        help='Disable converting positional only arguments to normal arguments',
        dest='convert_posargs_to_args',
    )
    minification_options.add_argument(
        '--no-preserve-shebang',
        action='store_false',
        help='Preserve any shebang line from the source',
        dest='preserve_shebang',
    )

    parser.add_argument('--version', '-v', action='version', version=version)

    args = parser.parse_args()

    # Handle some invalid argument combinations
    if '-' in args.path and len(args.path) != 1:
        sys.stderr.write('error: multiple path arguments, reading from stdin not allowed\n')
        sys.exit(1)
    if '-' in args.path and args.in_place:
        sys.stderr.write('error: reading from stdin, --in-place is not valid\n')
        sys.exit(1)
    if len(args.path) > 1 and not args.in_place:
        sys.stderr.write('error: multiple path arguments, --in-place required\n')
        sys.exit(1)
    if len(args.path) == 1 and os.path.isdir(args.path[0]) and not args.in_place:
        sys.stderr.write('error: path ' + args.path[0] + ' is a directory, --in-place required\n')
        sys.exit(1)

    return args

def source_modules(args):

    def error(os_error):
        raise os_error

    for path_arg in args.path:
        if os.path.isdir(path_arg):
            for root, dirs, files in os.walk(path_arg, onerror=error, followlinks=True):
                for file in files:
                    if file.endswith('.py'):
                        yield os.path.join(root, file)
        else:
            yield path_arg

def do_minify(source, filename, minification_args):

    preserve_globals = []
    if minification_args.preserve_globals:
        for arg in minification_args.preserve_globals:
            names = [name.strip() for name in arg.split(',') if name]
            preserve_globals.extend(names)

    preserve_locals = []
    if minification_args.preserve_locals:
        for arg in minification_args.preserve_locals:
            names = [name.strip() for name in arg.split(',') if name]
            preserve_locals.extend(names)

    return minify(
        source,
        filename=filename,
        combine_imports=minification_args.combine_imports,
        remove_pass=minification_args.remove_pass,
        remove_annotations=minification_args.remove_annotations,
        remove_literal_statements=minification_args.remove_literal_statements,
        hoist_literals=minification_args.hoist_literals,
        rename_locals=minification_args.rename_locals,
        preserve_locals=preserve_locals,
        rename_globals=minification_args.rename_globals,
        preserve_globals=preserve_globals,
        remove_object_base=minification_args.remove_object_base,
        convert_posargs_to_args=minification_args.convert_posargs_to_args,
        preserve_shebang=minification_args.preserve_shebang
    )


if __name__ == '__main__':
    main()
