import ast
import math

from python_minifier.expression_printer import ExpressionPrinter
from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_ast_node


class FoldConstants(SuiteTransformer):
    """
    Fold Constants if it would reduce the size of the source
    """

    def __init__(self):
        super(FoldConstants, self).__init__()

    def visit_BinOp(self, node):

        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # Check this is a constant expression that could be folded
        if not is_ast_node(node.left, (ast.Num, ast.Str, 'Bytes', 'NameConstant')):
            return node
        if not is_ast_node(node.right, (ast.Num, ast.Str, 'Bytes', 'NameConstant')):
            return node

        expression_printer = ExpressionPrinter()

        try:
            original_expression = expression_printer(node)
            value = eval(original_expression)
        except Exception as e:
            return node

        if math.isnan(value):
            # There is no nan literal.
            new_node = ast.Call(func=ast.Name('float', ctx=ast.Load()), args=[ast.Str('nan')], keywords=[])
        elif isinstance(value, str):
            new_node = ast.Str(s=value)
        elif isinstance(value, bytes):
            new_node = ast.Bytes(s=value)
        elif isinstance(value, bool):
            new_node = ast.NameConstant(value=value)
        elif isinstance(value, (int, float, complex)):
            if repr(value).startswith('-'):
                # Represent negative numbers as a USub UnaryOp, so that the ast roundtrip is correct
                new_node = ast.UnaryOp(op=ast.USub(), operand=ast.Num(n=-value))
            else:
                new_node = ast.Num(n=value)
        else:
            return node

        expression_printer = ExpressionPrinter()
        folded_expression = expression_printer(new_node)

        if len(folded_expression) > len(original_expression):
            # Result is longer than original expression
            return node

        assert eval(folded_expression) == value

        # Some complex number values are parsed as a BinOp
        # Make sure we represent our AST the same way so it roundtrips correctly
        parsed_folded_expression = ast.parse(folded_expression, 'folded expression', 'eval')
        assert isinstance(parsed_folded_expression, ast.Expression)
        if isinstance(parsed_folded_expression.body, ast.BinOp):
            new_node = parsed_folded_expression.body

        return self.add_child(new_node, node.parent, node.namespace)
