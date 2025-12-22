import python_minifier.ast_compat as ast

from hypothesis.strategies import SearchStrategy, composite, lists, one_of, recursive, sampled_from

from .expressions import NameConstant, Num

leaves = one_of(
    NameConstant(),
    Num()
)


@composite
def BinOp(draw, expression) -> ast.BinOp:
    op = draw(
        sampled_from(
            [
                ast.Add(),      # Most common arithmetic
                ast.Sub(),
                ast.Mult(),
                ast.Div(),
                ast.Mod(),      # Common operations
                ast.FloorDiv(),
                ast.Pow(),      # Less common
                ast.BitAnd(),   # Bitwise operations
                ast.BitOr(),
                ast.BitXor(),
                ast.LShift(),
                ast.RShift(),
                ast.MatMult()   # Least common (matrix mult)
            ]
        )
    )

    le = draw(lists(expression, min_size=2, max_size=2))

    return ast.BinOp(le[0], op, le[1])


@composite
def UnaryOp(draw, expression) -> ast.UnaryOp:
    op = draw(
        sampled_from(
            [
                ast.USub(),     # Unary minus: -x
                ast.UAdd(),     # Unary plus: +x
                ast.Invert(),   # Bitwise not: ~x
                ast.Not(),      # Logical not: not x
            ]
        )
    )

    operand = draw(expression)

    return ast.UnaryOp(op, operand)


def expression() -> SearchStrategy:
    return recursive(
        leaves,
        lambda expression:
        one_of(BinOp(expression), UnaryOp(expression)),
        max_leaves=150
    )


@composite
def FoldableExpression(draw) -> ast.Expression:
    """ An eval expression """
    e = draw(expression())
    return ast.Expression(e)
