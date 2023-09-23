import python_minifier.ast_compat as ast
import sys

from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_ast_node


class RemoveDebug(SuiteTransformer):
    """
    Remove if statements where the condition tests __debug__ is True

    If a statement is syntactically necessary, use an empty expression instead
    """

    def __call__(self, node):
        return self.visit(node)

    def constant_value(self, node):
        if sys.version_info < (3, 4):
            return node.id == 'True'
        elif is_ast_node(node, 'NameConstant'):
            return node.value
        return None

    def can_remove(self, node):
        if not isinstance(node, ast.If):
            return False

        if isinstance(node.test, ast.Name) and node.test.id == '__debug__':
            return True

        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Is) and self.constant_value(node.test.comparators[0]) is True:
            return True

        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.IsNot) and self.constant_value(node.test.comparators[0]) is False:
            return True

        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq) and self.constant_value(node.test.comparators[0]) is True:
            return True

        return False

    def suite(self, node_list, parent):

        without_debug = [self.visit(a) for a in filter(lambda n: not self.can_remove(n), node_list)]

        if len(without_debug) == 0:
            if isinstance(parent, ast.Module):
                return []
            else:
                return [self.add_child(ast.Expr(value=ast.Num(0)), parent=parent)]

        return without_debug
