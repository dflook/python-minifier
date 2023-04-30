import ast
import sys

from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_ast_node


class RemoveExplicitReturnNone(SuiteTransformer):
    def __call__(self, node):
        return self.visit(node)

    def visit_Return(self, node):
        assert isinstance(node, ast.Return)

        # Transform `return None` -> `return`

        if sys.version_info < (3, 4) and isinstance(node.value, ast.Name) and node.value.id == 'None':
            node.value = None

        elif sys.version_info >= (3, 4) and is_ast_node(node.value, 'NameConstant') and node.value.value is None:
            node.value = None

        return node

    def visit_FunctionDef(self, node):
        assert is_ast_node(node, (ast.FunctionDef, 'AsyncFunctionDef'))

        node.body = [self.visit(a) for a in node.body]

        # Remove an explicit valueless `return` from the end of a function
        if len(node.body) > 0 and isinstance(node.body[-1], ast.Return) and node.body[-1].value is None:
            node.body.pop()

        # Replace empty suites with `0` expression statements
        if len(node.body) == 0:
            node.body = [self.add_child(ast.Expr(value=ast.Num(0)), parent=node)]

        return node
