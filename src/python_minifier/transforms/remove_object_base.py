import ast

from python_minifier.transforms.suite_transformer import SuiteTransformer


class RemoveObject(SuiteTransformer):
    def __init__(self, min_python_version):
        self.min_python_version = min_python_version

    def __call__(self, node):
        if self.min_python_version < (3, 0):
            return node

        return self.visit(node)

    def visit_ClassDef(self, node):
        node.bases = [
            b for b in node.bases if not isinstance(b, ast.Name) or (isinstance(b, ast.Name) and b.id != 'object')
        ]

        node.body = [self.visit(n) for n in node.body]

        return node
