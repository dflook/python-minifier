import ast

from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.rename.mapper import add_parent


class RemovePass(SuiteTransformer):
    """
    Remove Pass keywords from source

    If a statement is syntactically necessary, use an empty expression instead
    """

    def __call__(self, node):
        return self.visit(node)

    def suite(self, node_list, parent):
        without_pass = [self.visit(a) for a in filter(lambda n: not isinstance(n, ast.Pass), node_list)]

        if len(without_pass) == 0:
            if isinstance(parent, ast.Module):
                return []
            else:
                expr = ast.Expr(value=ast.Num(0))
                add_parent(expr, parent=parent, namespace=parent.namespace)
                return [expr]

        return without_pass
