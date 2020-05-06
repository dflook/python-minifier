import ast
import sys

from python_minifier.transforms.suite_transformer import SuiteTransformer


class RemoveObject(SuiteTransformer):
    def __call__(self, node):
        if sys.version_info < (3, 0):
            return node

        return self.visit(node)

    def visit_ClassDef(self, node):
        node.bases = [
            b for b in node.bases if not isinstance(b, ast.Name) or (isinstance(b, ast.Name) and b.id != 'object')
        ]

        node.body = [self.visit(n) for n in node.body]

        return node
