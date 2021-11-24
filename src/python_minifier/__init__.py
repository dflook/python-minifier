"""
This package transforms python source code strings or ast.Module Nodes into
a 'minified' representation of the same source code.

"""

import ast
import os
import shutil

from python_minifier.ast_compare import CompareError, compare_ast
from python_minifier.module_printer import ModulePrinter
from python_minifier.rename import (
    rename_literals,
    bind_names,
    resolve_names,
    rename,
    allow_rename_globals,
    allow_rename_locals,
    add_namespace,
)
from python_minifier.transforms.combine_imports import CombineImports
from python_minifier.transforms.remove_annotations import RemoveAnnotations
from python_minifier.transforms.remove_literal_statements import RemoveLiteralStatements
from python_minifier.transforms.remove_object_base import RemoveObject
from python_minifier.transforms.remove_pass import RemovePass
from python_minifier.transforms.remove_posargs import remove_posargs
from python_minifier.util import ignore_dir, ignore_file


class UnstableMinification(RuntimeError):
    """
    Raised when a minified module differs from the original module in an unexpected way.

    This is raised when the minifier generates source code that doesn't parse back into the
    original module (after known transformations).
    This should never occur and is a bug.

    """

    def __init__(self, exception, source, minified):
        self.exception = exception
        self.source = source
        self.minified = minified

    def __str__(self):
        return 'Minification was unstable! Please create an issue at https://github.com/dflook/python-minifier/issues'


def minify(
    source,
    filename=None,
    remove_annotations=True,
    remove_pass=True,
    remove_literal_statements=False,
    combine_imports=True,
    hoist_literals=True,
    rename_locals=True,
    preserve_locals=None,
    rename_globals=False,
    preserve_globals=None,
    remove_object_base=True,
    convert_posargs_to_args=True,
):
    """
    Minify a python module

    The module is transformed according the the arguments.
    If all transformation arguments are False, no transformations are made to the AST, the returned string will
    parse into exactly the same module.

    Using the default arguments only transformations that are always or almost always safe are enabled.

    :param str source: The python module source code
    :param str filename: The original source filename if known

    :param bool remove_annotations: If type annotations should be removed where possible
    :param bool remove_pass: If Pass statements should be removed where possible
    :param bool remove_literal_statements: If statements consisting of a single literal should be removed, including docstrings
    :param bool combine_imports: Combine adjacent import statements where possible
    :param bool hoist_literals: If str and byte literals may be hoisted to the module level where possible.
    :param bool rename_locals: If local names may be shortened
    :param preserve_locals: Locals names to leave unchanged when rename_locals is True
    :type preserve_locals: list[str]
    :param bool rename_globals: If global names may be shortened
    :param preserve_globals: Global names to leave unchanged when rename_globals is True
    :type preserve_globals: list[str]
    :param bool remove_object_base: If object as a base class may be removed
    :param bool convert_posargs_to_args: If positional-only arguments will be converted to normal arguments

    :rtype: str

    """
    minifier = Minifier(
        remove_annotations,
        remove_pass,
        remove_literal_statements,
        combine_imports,
        hoist_literals,
        rename_locals,
        preserve_locals,
        rename_globals,
        preserve_globals,
        remove_object_base,
        convert_posargs_to_args,
    )
    return minifier.minify(source, filename)


class Minifier(object):
    def __init__(
        self,
        remove_annotations=True,
        remove_pass=True,
        remove_literal_statements=False,
        combine_imports=True,
        hoist_literals=True,
        rename_locals=True,
        preserve_locals=None,
        rename_globals=False,
        preserve_globals=None,
        remove_object_base=True,
        convert_posargs_to_args=True,
    ):
        """Class for minifying python modules.

        The module is transformed according the the arguments.
        If all transformation arguments are False, no transformations are made to the AST, the returned string will
        parse into exactly the same module.

        Using the default arguments only transformations that are always or almost always safe are enabled.

        :param bool remove_annotations: If type annotations should be removed where possible
        :param bool remove_pass: If Pass statements should be removed where possible
        :param bool remove_literal_statements: If statements consisting of a single literal should be removed, including docstrings
        :param bool combine_imports: Combine adjacent import statements where possible
        :param bool hoist_literals: If str and byte literals may be hoisted to the module level where possible.
        :param bool rename_locals: If local names may be shortened
        :param preserve_locals: Locals names to leave unchanged when rename_locals is True
        :type preserve_locals: list[str]
        :param bool rename_globals: If global names may be shortened
        :param preserve_globals: Global names to leave unchanged when rename_globals is True
        :type preserve_globals: list[str]
        :param bool remove_object_base: If object as a base class may be removed
        :param bool convert_posargs_to_args: If positional-only arguments will be converted to normal arguments

        """
        self.remove_annotations = remove_annotations
        self.remove_pass = remove_pass
        self.remove_literal_statements = remove_literal_statements
        self.combine_imports = combine_imports
        self.hoist_literals = hoist_literals
        self.rename_locals = rename_locals
        self.preserve_locals = preserve_locals
        self.rename_globals = rename_globals
        self.preserve_globals = preserve_globals
        self.remove_object_base = remove_object_base
        self.convert_posargs_to_args = convert_posargs_to_args

    def minify(self, source, filename=None):
        """Minify a python module.

        :param bytes source: The python module source code. If a str, will be encoded to bytes.
        :param str filename: The original source filename if known

        :rtype: str
        """
        if isinstance(source, str):
            source.encode()

        filename = filename or 'python_minifier.minify source'

        # This will raise if the source file can't be parsed
        module = ast.parse(source, filename)

        add_namespace(module)

        if self.remove_literal_statements:
            module = RemoveLiteralStatements()(module)

        if self.combine_imports:
            module = CombineImports()(module)

        if self.remove_annotations:
            module = RemoveAnnotations()(module)

        if self.remove_pass:
            module = RemovePass()(module)

        if self.remove_object_base:
            module = RemoveObject()(module)

        bind_names(module)
        resolve_names(module)

        if module.tainted:
            rename_globals = False
            rename_locals = False
        else:
            rename_globals = self.rename_globals
            rename_locals = self.rename_locals

        allow_rename_locals(module, rename_locals, self.preserve_locals)
        allow_rename_globals(module, rename_globals, self.preserve_globals)

        if self.hoist_literals:
            rename_literals(module)

        rename(module, prefix_globals=not rename_globals, preserved_globals=self.preserve_globals)

        if self.convert_posargs_to_args:
            module = remove_posargs(module)

        return unparse(module)

    def minify_buffer(self, f, filename=None):
        """Minify a readable buffer.

        :param f: Readable buffer.
        :param str filename: If known, the name of the file wrapped by the buffer.
        :rtype: str
        """
        return self.minify(f.read(), filename)

    def minify_file(self, path):
        """Minify the contents of a file.

        :param str path: Path to file.
        :rtype: str
        """
        with open(path, "rb") as f:
            return self.minify_buffer(f, path)

    def minify_dir(self, in_path, out_path, copy_nonpy=False, force=False):
        """Recursively minify a directory of python files.

        :param str in_path: Path to directory of existing python files.
        :param str out_path: Path to directory where minified files will be written.
        :param bool copy_nonpy: Copy files other than *.py from the in to the out directory.
            Some file extensions (e.g. cached bytecode) will be ignored.
            Default False.
        :param bool force: If the out_dir is not empty, delete it.
            Ignored if in_dir == out_dir.
            Default False.
        """
        in_path = os.path.abspath(in_path)
        out_path = os.path.abspath(out_path)

        if in_path == out_path:
            copy_nonpy = False
        else:
            if os.path.exists(out_path) and os.listdir(out_path):
                if force:
                    shutil.rmtree(out_path)
                else:
                    raise FileExistsError('Non-empty target directory already exists')

        def truncate(p):
            return p[len(in_path):].lstrip(os.sep)

        py_paths = []
        nonpy_paths = []
        dirs = {out_path}

        for root, dpaths, fpaths in os.walk(in_path):
            rel_root = truncate(root)
            has_files = False

            for fpath in fpaths:
                rel_fpath = os.path.join(rel_root, fpath)
                if fpath.endswith('.py'):
                    py_paths.append(rel_fpath)
                    has_files = True
                elif copy_nonpy and not ignore_file(fpath):
                    nonpy_paths.append(rel_fpath)
                    has_files = True

            if has_files:
                dirs.add(rel_root)

            to_ignore = []

            for idx, dpath in enumerate(dpaths):
                if ignore_dir(dpath):
                    to_ignore.append(idx)

            for idx in reversed(to_ignore):
                dpaths.pop(idx)

        print(dirs)
        for dpath in dirs:
            os.makedirs(os.path.join(out_path, dpath), exist_ok=True)
            print(os.path.join(out_path, dpath))

        for path in py_paths:
            s = self.minify_file(os.path.join(in_path, path))
            with open(os.path.join(out_path, path), "w") as f:
                f.write(s)

        for path in nonpy_paths:
            shutil.copyfile(
                os.path.join(in_path, path),
                os.path.join(out_path, path),
            )


def unparse(module):
    """
    Turn a module AST into python code

    This returns an exact representation of the given module,
    such that it can be parsed back into the same AST.

    :param module: The module to turn into python code
    :type: module: :class:`ast.Module`
    :rtype: str

    """

    assert isinstance(module, ast.Module)

    printer = ModulePrinter()
    printer(module)

    try:
        minified_module = ast.parse(printer.code, 'python_minifier.unparse output')
    except SyntaxError as syntax_error:
        raise UnstableMinification(syntax_error, '', printer.code)

    try:
        compare_ast(module, minified_module)
    except CompareError as compare_error:
        raise UnstableMinification(compare_error, '', printer.code)

    return printer.code


def awslambda(source, filename=None, entrypoint=None):
    """
    Minify a python module for use as an AWS Lambda function

    This returns a string suitable for embedding in a cloudformation template.
    When minifying, all transformations are enabled.

    :param str source: The python module source code
    :param str filename: The original source filename if known
    :param entrypoint: The lambda entrypoint function
    :type entrypoint: str or NoneType
    :rtype: str

    """

    rename_globals = True
    if entrypoint is None:
        rename_globals = False

    return minify(
        source, filename, remove_literal_statements=True, rename_globals=rename_globals, preserve_globals=[entrypoint],
    )
