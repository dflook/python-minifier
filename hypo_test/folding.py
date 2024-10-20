import ast

from hypothesis.strategies import SearchStrategy, composite, lists, recursive, sampled_from

from .expressions import NameConstant, Num

leaves = NameConstant() | Num()


@composite
def BinOp(draw, expression) -> ast.BinOp:
    op = draw(
        sampled_from(
            [
                ast.Add(),
                ast.Sub(),
                ast.Mult(),
                ast.Div(),
                ast.FloorDiv(),
                ast.Mod(),
                ast.Pow(),
                ast.LShift(),
                ast.RShift(),
                ast.BitOr(),
                ast.BitXor(),
                ast.BitAnd(),
                ast.MatMult()
            ]
        )
    )

    le = draw(lists(expression, min_size=2, max_size=2))

    return ast.BinOp(le[0], op, le[1])


def expression() -> SearchStrategy:
    return recursive(
        leaves,
        lambda expression:
        BinOp(expression),
        max_leaves=150
    )


@composite
def FoldableExpression(draw) -> ast.Expression:
    """ An eval expression """
    e = draw(expression())
    return ast.Expression(e)
