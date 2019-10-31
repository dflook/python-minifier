import ast

from python_minifier.rename.mapper import add_parent
from python_minifier.transforms.suite_transformer import SuiteTransformer


def find_doc(node):

    if isinstance(node, ast.Attribute):
        if node.attr == '__doc__':
            raise ValueError('__doc__ found!')

    for child in ast.iter_child_nodes(node):
        find_doc(child)


def _doc_in_module(module):
    try:
        find_doc(module)
        return False
    except:
        return True

class RemoveLiteralStatements(SuiteTransformer):
    """
    Remove literal expressions from the code

    This includes docstrings
    """

    def __call__(self, node):
        if _doc_in_module(node):
            return node
        return self.visit(node)

    def visit_Module(self, node):
        for binding in node.bindings:
            if binding.name == '__doc__':
                node.body = [self.visit(a) for a in node.body]
                return node

        node.body = self.suite(node.body, parent=node)
        return node

    def is_literal_statement(self, node):
        if not isinstance(node, ast.Expr):
            return False

        if (
            isinstance(node.value, (ast.Num, ast.Str, ast.NameConstant))
            or node.value.__class__.__name__ == 'Constant'
            or node.value.__class__.__name__ == 'Bytes'
        ):
            return True

        return False

    def suite(self, node_list, parent):
        without_literals = [self.visit(a) for a in filter(lambda n: not self.is_literal_statement(n), node_list)]

        if len(without_literals) == 0:
            if isinstance(parent, ast.Module):
                return []
            else:
                expr = ast.Expr(value=ast.Num(0))
                add_parent(expr, parent=parent, namespace=parent.namespace)
                return [expr]

        return without_literals
