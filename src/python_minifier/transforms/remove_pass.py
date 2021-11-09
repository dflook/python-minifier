import ast

from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_ast_node


class RemovePass(SuiteTransformer):
    """
    Remove Pass keywords from source

    If a statement is syntactically necessary, use an empty expression instead
    """

    def __call__(self, node):
        return self.visit(node)

    def suite(self, node_list, parent):
        without_pass = [self.visit(a) for a in filter(lambda n: not is_ast_node(n, ast.Pass), node_list)]

        if len(without_pass) == 0:
            if isinstance(parent, ast.Module):
                return []
            else:
                return [self.add_child(ast.Expr(value=ast.Num(0)), parent=parent)]

        return without_pass
