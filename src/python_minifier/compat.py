import ast
from python_minifier.util import NodeVisitor


class PythonSourceCompatability(NodeVisitor):
    """
    Determine the minimum python version that can parse this source

    It may or may not be parsable by more recent versions of python.

    The AST will have been parsed by the current version of python.

    This only cares about syntax features.
    """

    class Version(Exception):
        def __init__(self, version):
            self.version = version

    def __init__(self):
        self._min_version = 2, 7

    def set_minimum(self, major, minor):
        if (major, minor) > self._min_version:
            self._min_version = major, minor

    def set_version(self, major, minor):
        raise self.Version((major, minor))

    def __call__(self, module):
        assert isinstance(module, ast.Module)

        try:
            self.visit(module)
            return self._min_version
        except self.Version as v:
            return v.version

    # region Literals
    def visit_JoinedStr(self, node):
        self.set_minimum(3, 6)
        self.generic_visit(node)
    # endregion

    # region Expressions
    def visit_NamedExpr(self, node):
        self.set_minimum(3, 8)
        self.generic_visit(node)

    def visit_MatMult(self, node):
        self.set_minimum(3, 5)
        self.generic_visit(node)
    # endregion

    # region Assignments
    def visit_AnnAssign(self, node):
        self.set_minimum(3, 6)
        self.generic_visit(node)
    # endregion

    # region Function and Class definitions
    def visit_arguments(self, node):
        if getattr(node, 'posonlyargs', []):
            self.set_minimum(3, 8)

        if getattr(node, 'kwonlyargs', []):
            self.set_minimum(3, 0)

        if getattr(node, 'varargannotation', None):
            self.set_minimum(3, 0)

        if getattr(node, 'kwargannotation', None):
            self.set_minimum(3, 0)

        self.generic_visit(node)

    def visit_arg(self, node):
        if getattr(node, 'annotation'):
            self.set_minimum(3, 0)

    def visit_YieldFrom(self, node):
        self.set_minimum(3, 3)
        self.generic_visit(node)

    def visit_nonlocal(self, node):
        self.set_minimum(3, 0)
        self.generic_visit(node)
    # endregion

    # region Async and await
    def visit_AsyncFunctionDef(self, node):
        self.set_minimum(3, 5)
        self.generic_visit(node)

    def visit_Await(self, node):
        self.set_minimum(3, 5)
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.set_minimum(3, 5)
        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        self.set_minimum(3, 5)
        self.generic_visit(node)
    # endregion

    # region Pattern Matching
    def visit_Match(self, node):
        self.set_minimum(3, 10)
        self.generic_visit(node)
    # endregion

    def visit_Repr(self, node):
        self.set_version(2, 7)
        self.generic_visit(node)

    def visit_comprehension(self, node):
        if getattr(node, 'is_async', False):
            self.set_version(3, 6)
        self.generic_visit(node)


def python_source_compat(module):
    return PythonSourceCompatability()(module)
