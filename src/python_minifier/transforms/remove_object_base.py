import python_minifier.ast_compat as ast
import sys

from python_minifier.transforms.suite_transformer import SuiteTransformer


class RemoveObject(SuiteTransformer):
    def __call__(self, node):
        return self.visit(node)

    def visit_ClassDef(self, node):
        node.bases = [
            b for b in node.bases if not isinstance(b, ast.Name) or (isinstance(b, ast.Name) and b.id != 'object')
        ]

        if hasattr(node, 'type_params') and node.type_params is not None:
            node.type_params = [self.visit(t) for t in node.type_params]

        node.body = [self.visit(n) for n in node.body]

        return node
