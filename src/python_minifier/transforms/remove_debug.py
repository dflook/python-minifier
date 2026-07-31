import sys

import python_minifier.ast_compat as ast

from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_constant_node


class RemoveDebug(SuiteTransformer):
    """
    Mark if statements whose condition tests __debug__ is True as dead

    The marked statements are removed by the RemoveDeadBranches transform, which
    keeps any else branch and any branch that can't be removed without changing
    the meaning of the program.
    """

    def __call__(self, node):
        return self.visit(node)

    def constant_value(self, node):
        if sys.version_info < (3, 4):
            # True and False are Name nodes before python 3.4.
            # The comparator may be any expression, so check it is a Name.
            if isinstance(node, ast.Name) and node.id in ('True', 'False'):
                return node.id == 'True'
            return None
        elif is_constant_node(node, ast.NameConstant):
            return node.value
        return None

    def can_remove(self, node):
        if not isinstance(node, ast.If):
            return False

        def is_simple_debug_check():
            # Simple case: if __debug__:
            if isinstance(node.test, ast.Name) and node.test.id == '__debug__':
                return True
            return False

        def is_truthy_debug_comparison():
            # Comparison case: if __debug__ is True / False / etc.
            if not isinstance(node.test, ast.Compare):
                return False

            if not isinstance(node.test.left, ast.Name):
                return False

            if node.test.left.id != '__debug__':
                return False

            if len(node.test.ops) == 1:
                op = node.test.ops[0]
                comparator_value = self.constant_value(node.test.comparators[0])

                if isinstance(op, ast.Is) and comparator_value is True:
                    return True
                if isinstance(op, ast.IsNot) and comparator_value is False:
                    return True
                if isinstance(op, ast.Eq) and comparator_value is True:
                    return True

            return False

        if is_simple_debug_check() or is_truthy_debug_comparison():
            return True
        return False

    def visit_If(self, node):
        assert isinstance(node, ast.If)

        if self.can_remove(node):
            node.resolved_test = False

        return self.generic_visit(node)
