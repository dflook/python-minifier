import ast

from python_minifier.ast_compare import AstComparer, CompareError
from python_minifier.module_printer import ModulePrinter


class UnstableMinification(RuntimeError):
    def __init__(self, exception, source, minified):
        self.exception = exception
        self.source = source
        self.minified = minified

    def __str__(self):
        return 'Minification was unstable! Please create an issue at https://github.com/dflook/python-minifier/issues'


def minify(source, filename=None):
    """
    Minify a python module

    With the default arguments an exact representation of the input source is returned.

    :param str source: The python module to minify
    :param str filename: The original source filename if known
    :rtype: str

    """

    filename = filename or 'python_minifer.minify source'

    # This will raise if the source file can't be parsed
    module = ast.parse(source, filename)

    printer = ModulePrinter()
    printer(module)

    try:
        minified_module = ast.parse(printer.code, 'python_minifier.minify output')
    except SyntaxError as syntax_error:
        raise UnstableMinification(syntax_error, source, printer.code)

    try:
        comparer = AstComparer()
        comparer.compare(module, minified_module)
    except CompareError as compare_error:
        raise UnstableMinification(compare_error, source, printer.code)

    return printer.code


def awslambda(source, filename=None):
    """
    Minify a python module for use as an AWS Lambda function

    This returns a string suitable for embedding in a cloudformation template.

    :param str source: The python module to minify
    :param str filename: The original source filename if known
    :rtype: str

    """

    return minify(source, filename)
