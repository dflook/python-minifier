from __future__ import print_function
import argparse

import sys

from python_minifier import minify

from pkg_resources import get_distribution, DistributionNotFound
try:
    version = get_distribution('python_minifier').version
except DistributionNotFound:
    version = '0.0.0'

def main():

    parser = argparse.ArgumentParser(description='Minify Python source')

    parser.add_argument('path', type=str, help='The source file to minify. Use "-" to read from stdin')

    parser.add_argument('--no-combine-imports', action='store_false', help='Disable combining adjacent import statements', dest='combine_imports')
    parser.add_argument('--no-remove-pass', action='store_false', default=True, help='Disable removing Pass statements', dest='remove_pass')
    parser.add_argument('--remove-literal-statements', action='store_true', help='Enable removing statements that are just a literal (including docstrings)', dest='remove_literal_statements')
    parser.add_argument('--no-remove-annotations', action='store_false', help='Disable removing function and variable annotations', dest='remove_annotations')
    parser.add_argument('--no-hoist-literals', action='store_false', help='Disable replacing string and bytes literals with variables', dest='hoist_literals')

    parser.add_argument('-v', '--version', action='version', version=version)

    args = parser.parse_args()

    if args.path is '-':
        source = sys.stdin.read()
    else:
        with open(args.path, 'rb') as f:
            source = f.read()

    print(minify(
        source,
        filename=args.path,
        combine_imports=args.combine_imports,
        remove_pass=args.remove_pass,
        remove_literal_statements=args.remove_literal_statements,
        hoist_literals=args.hoist_literals
    ))

if __name__ == '__main__':
    main()
