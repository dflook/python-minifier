import ast
import sys

from python_minifier.transforms.suite_transformer import SuiteTransformer


class UseEqualsSpecifier(SuiteTransformer):
    """
    Use f string = specifiers

    Replaces manual = specifiers with the f string = specifier
    """

    def __call__(self, node):
        if sys.version_info < (3, 8):
            return node
        return self.visit(node)


    def visit_BinOp(self, node):
        # Make sure the constant is a string added with a value added to it
        if isinstance(node.op, ast.Add) and isinstance(node.left.value, str) and node.left.value[-1] == "=" and isinstance(node.right, ast.Name):

            # Make sure that the string is talking about the variable
            if not node.left.value == f'{node.right.id}=':
                return node

            return ast.parse('f"{' + node.right.id + '=}"')

        return node