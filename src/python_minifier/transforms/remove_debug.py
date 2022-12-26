import ast

from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_ast_node


class RemoveDebug(SuiteTransformer):
    """
    Remove if statements where the condition tests __debug__ is True

    If a statement is syntactically necessary, use an empty expression instead
    """

    def __call__(self, node):
        return self.visit(node)

    def can_remove(self, node):
        if not isinstance(node, ast.If):
            return False

        if is_ast_node(node.test, ast.Name) and node.test.id == '__debug__':
            return True

        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Is) and is_ast_node(node.test.comparators[0], ast.NameConstant) and node.test.comparators[0].value is True:
            return True

        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.IsNot) and is_ast_node(node.test.comparators[0], ast.NameConstant) and node.test.comparators[0].value is False:
            return True

        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq) and is_ast_node(node.test.comparators[0], ast.NameConstant) and node.test.comparators[0].value is True:
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
