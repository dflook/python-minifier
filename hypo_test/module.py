import ast

from hypothesis import assume
from hypothesis.strategies import integers, lists, sampled_from, recursive, none, booleans, SearchStrategy, composite, one_of

from hypo_test.expressions import Name, expression, name
from expressions import arguments

@composite
def Assign(draw) -> ast.Assign:
    targets = draw(lists(Name(ast.Store), min_size=1, max_size=3))
    return ast.Assign(targets=targets, value=draw(expression()))

@composite
def AnnAssign(draw) -> ast.AnnAssign:
    target = draw(Name(ast.Store))
    return ast.AnnAssign(target=target, annotation=draw(expression()), value=draw(expression()), simple=True)

@composite
def AugAssign(draw):
    op = draw(sampled_from([
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
        ast.BitOr(),
        ast.BitAnd(),
        ast.MatMult()
    ]))

    return ast.AugAssign(target=draw(Name(ast.Store)), op=op, value=draw(expression()))


@composite
def Print(draw):
    return ast.Print(dest=None, value=draw(expression()), nl=not draw(booleans()))

@composite
def Raise(draw):
    return ast.Raise(draw(none() | expression()), cause=None)

@composite
def Assert(draw):
    return ast.Assert(test=draw(expression()), msg=draw(expression()))

@composite
def Delete(draw):
    return ast.Delete(targets=draw(lists(expression(), min_size=1, max_size=3)))

@composite
def Pass(draw) -> ast.Pass:
    return ast.Pass()

@composite
def Break(draw) -> ast.Break:
    return ast.Break()

@composite
def Continue(draw) -> ast.Continue:
    return ast.Continue()

@composite
def With(draw, statements) -> ast.With:
    items = draw(lists(expression(), min_size=1, max_size=3))
    body = draw(lists(statements, min_size=1, max_size=3))
    return ast.With([ast.withitem(context_expr=i, optional_vars=None) for i in items], body)

@composite
def AsyncWith(draw, statements) -> ast.AsyncWith:
    items = draw(lists(expression(), min_size=1, max_size=3))
    body = draw(lists(statements, min_size=1, max_size=3))
    return ast.AsyncWith([ast.withitem(context_expr=i, optional_vars=None) for i in items], body)

@composite
def If(draw, statements) -> ast.If:
    body = draw(lists(statements, min_size=1, max_size=3))
    orelse = draw(lists(statements, min_size=1, max_size=3))
    return ast.If(test=draw(expression()), body=body, orelse=orelse)

@composite
def ExceptHandler(draw, statements) -> ast.ExceptHandler:
    t = draw(none() | Name())

    n = None
    if t is not None:
        n = draw(name())

    return ast.ExceptHandler(
        type=t,
        name=n,
        body=draw(lists(statements, min_size=1, max_size=3))
    )

@composite
def Try(draw, statements) -> ast.Try:
    body = draw(lists(statements, min_size=1, max_size=3))
    handlers = draw(lists(ExceptHandler(statements), min_size=0, max_size=2))
    if handlers:
        orelse = draw(lists(statements, min_size=1, max_size=3))
    else:
        orelse = []

    finalbody = draw(lists(statements, min_size=1, max_size=3))
    return ast.Try(
        body=body,
        handlers=handlers,
        orelse=orelse,
        finalbody=finalbody
    )

@composite
def For(draw, statements) -> ast.For:
    target = draw(Name(ast.Store))
    iter = draw(expression())
    body = draw(lists(statements, min_size=1, max_size=3))
    orelse = draw(lists(statements, min_size=1, max_size=3))
    return ast.For(target, iter, body, orelse)

@composite
def AsyncFor(draw, statements) -> ast.AsyncFor:
    target = draw(Name(ast.Store))
    iter = draw(expression())
    body = draw(lists(statements, min_size=1, max_size=3))
    orelse = draw(lists(statements, min_size=1, max_size=3))
    return ast.AsyncFor(target, iter, body, orelse)

@composite
def While(draw, statements) -> ast.While:
    test = draw(expression())
    body = draw(lists(statements, min_size=1, max_size=3))
    orelse = draw(lists(statements, min_size=1, max_size=3))
    return ast.While(test, body, orelse)

@composite
def Return(draw) -> ast.Return:
    return ast.Return(draw(expression()))

@composite
def Expr(draw) -> ast.Expr:
    return ast.Expr(draw(expression()))

@composite
def Global(draw) -> ast.Global:
    return ast.Global(draw(lists(name(), min_size=1, max_size=3)))

@composite
def Nonlocal(draw) -> ast.Nonlocal:
    return ast.Nonlocal(draw(lists(name(), min_size=1, max_size=3)))

@composite
def alias(draw) -> ast.alias:
    return ast.alias(name=draw(name()), asname=draw(none() | name()))

@composite
def Import(draw) -> ast.Import:
    return ast.Import(names=draw(lists(alias(), min_size=1, max_size=3)))

@composite
def ImportFrom(draw) -> ast.ImportFrom:
    return ast.ImportFrom(module=draw(name()),
                          names=draw(lists(alias(), min_size=1, max_size=3)),
                          level=draw(integers(min_value=0, max_value=2)))

@composite
def FunctionDef(draw, statements) -> ast.FunctionDef:
    n = draw(name())
    args = draw(arguments())
    body = draw(lists(statements, min_size=1, max_size=3))
    decorator_list = draw(lists(Name(), min_size=0, max_size=2))
    returns = draw(none() | expression())
    return ast.FunctionDef(n, args, body, decorator_list, returns)

@composite
def AsyncFunctionDef(draw, statements) -> ast.AsyncFunctionDef:
    n = draw(name())
    args = draw(arguments())
    body = draw(lists(statements, min_size=1, max_size=3))
    decorator_list = draw(lists(Name(), min_size=0, max_size=2))
    returns = draw(none() | expression())
    return ast.AsyncFunctionDef(n, args, body, decorator_list, returns)

@composite
def keyword(draw) -> ast.keyword:
    return ast.keyword(
        arg=draw(name()),
        value=draw(expression())
    )

@composite
def ClassDef(draw, statements) -> ast.ClassDef:
    n = draw(name())
    bases = draw(lists(expression(), min_size=0, max_size=2))
    keywords = draw(lists(keyword(), min_size=0, max_size=2))

    assume(len({kw.arg for kw in keywords}) == len(keywords))

    body = draw(lists(statements, min_size=1, max_size=3))
    decorator_list = draw(lists(Name(), min_size=0, max_size=2))
    return ast.ClassDef(
        name=n,
        bases=bases,
        keywords=keywords,
        body=body,
        decorator_list=decorator_list
    )

if hasattr(ast, 'Print'):
    simple_statements = one_of(
        Pass(),
        Break(),
        Continue(),
        Global(),
        Nonlocal(),
        Expr(),
        Assert(),
        Print(),
        Raise(),
        #Delete() |
        Assign(),
        AnnAssign(),
        AugAssign(),
        Import(),
        ImportFrom()
    )
else:
    simple_statements = one_of(
        Pass(),
        Break(),
        Continue(),
        Global(),
        Nonlocal(),
        Expr(),
        Assert(),
        Raise(),
        #Delete() |
        Assign(),
        AnnAssign(),
        AugAssign(),
        Import(),
        ImportFrom()
    )

def suite() -> SearchStrategy:
    return recursive(
        simple_statements,
        lambda statements:
            one_of(
                With(statements),
                AsyncWith(statements),
                If(statements),
                For(statements),
                AsyncFor(statements),
                While(statements),
                FunctionDef(statements),
                AsyncFunctionDef(statements),
                ClassDef(statements),
                Try(statements)
            ),
        max_leaves=150
    )

@composite
def Module(draw) -> ast.Module:
    b = draw(lists(suite(), min_size=1, max_size=10))
    return ast.Module(body=b, type_ignores=[])
