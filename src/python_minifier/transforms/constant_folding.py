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
        # We don't try to fold strings or bytes, since they have probably been arranged this way to make the source shorter and we are unlikely to beat that
        if not is_ast_node(node.left, (ast.Num, 'NameConstant')):
            return node
        if not is_ast_node(node.right, (ast.Num, 'NameConstant')):
            return node

        if isinstance(node.op, ast.Div):
            # Folding div is subtle, since it can have different results in Python 2 and Python 3
            # Do this once target version options have been implemented
            return node

        if isinstance(node.op, ast.Pow):
            # This can be folded, but it is unlikely to reduce the size of the source
            # It can also be slow to evaluate
            return node

        expression_printer = ExpressionPrinter()

        try:
            original_expression = expression_printer(node)
            globals = {}
            locals = {}
            value = eval(original_expression, globals, locals)
        except Exception as e:
            return node

        if isinstance(value, float) and math.isnan(value):
            # There is no nan literal.
            new_node = ast.Call(func=ast.Name(id='float', ctx=ast.Load()), args=[ast.Str(s='nan')], keywords=[])
        elif isinstance(value, bool):
            new_node = ast.NameConstant(value=value)
        elif isinstance(value, (int, float, complex)):
            try:
                if repr(value).startswith('-'):
                    # Represent negative numbers as a USub UnaryOp, so that the ast roundtrip is correct
                    new_node = ast.UnaryOp(op=ast.USub(), operand=ast.Num(n=-value))
                else:
                    new_node = ast.Num(n=value)
            except Exception:
                # repr(value) failed, most likely due to some limit
                return node
        else:
            return node

        expression_printer = ExpressionPrinter()
        folded_expression = expression_printer(new_node)

        if len(folded_expression) >= len(original_expression):
            # Result is not shorter than original expression
            return node

        try:
            globals = {'__builtins__': {'float': float}}
            locals = {}
            folded_value = eval(folded_expression, globals, locals)
        except NameError as ne:
            if ne.name in ['inf', 'infj', 'nan']:
                # When the value is something like inf+0j the expression printer will print it that way, which is not valid Python.
                # In python code it should be '1e999+0j', which parses as a BinOp that the expression printer can handle.
                # It's not worth fixing the expression printer to handle this case, since it is unlikely to occur in real code.
                return node
            raise

        if isinstance(value, float) and math.isnan(value):
            assert math.isnan(folded_value)
        else:
            assert folded_value == value and type(folded_value) == type(value)

        #print(f'{original_expression=}')
        #print(f'{folded_expression=}')

        return self.add_child(new_node, node.parent, node.namespace)
