import python_minifier.ast_compat as ast

from hypothesis.strategies import SearchStrategy, booleans, composite, integers, lists, none, one_of, recursive, sampled_from

from .expressions import Name, arguments, expression, name


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

    return ast.AugAssign(target=draw(Name(ast.Store)), op=op, value=draw(expression()))


@composite
def Print(draw):
    return ast.Print(dest=None, value=draw(expression()), nl=not draw(booleans()))


@composite
def Raise(draw):
    return ast.Raise(draw(one_of(none(), expression())), cause=None)


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
    # Tuples cannot be context expressions - they parse as multiple withitems
    items = draw(lists(expression().filter(lambda e: not isinstance(e, ast.Tuple)), min_size=1, max_size=3))
    body = draw(lists(statements, min_size=1, max_size=3))
    return ast.With([ast.withitem(context_expr=i, optional_vars=None) for i in items], body)


@composite
def AsyncWith(draw, statements) -> ast.AsyncWith:
    # Tuples cannot be context expressions - they parse as multiple withitems
    items = draw(lists(expression().filter(lambda e: not isinstance(e, ast.Tuple)), min_size=1, max_size=3))
    body = draw(lists(statements, min_size=1, max_size=3))
    return ast.AsyncWith([ast.withitem(context_expr=i, optional_vars=None) for i in items], body)


@composite
def If(draw, statements) -> ast.If:
    body = draw(lists(statements, min_size=1, max_size=3))
    orelse = draw(lists(statements, min_size=1, max_size=3))
    return ast.If(test=draw(expression()), body=body, orelse=orelse)


@composite
def ExceptHandler(draw, statements) -> ast.ExceptHandler:
    t = draw(one_of(none(), Name()))

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
    return ast.alias(name=draw(name()), asname=draw(one_of(none(), name())))


@composite
def Import(draw) -> ast.Import:
    return ast.Import(names=draw(lists(alias(), min_size=1, max_size=3)), is_lazy=draw(sampled_from([0, 1])))


@composite
def ImportFrom(draw) -> ast.ImportFrom:
    return ast.ImportFrom(
        module=draw(name()),
        names=draw(lists(alias(), min_size=1, max_size=3)),
        level=draw(integers(min_value=0, max_value=2)),
        is_lazy=draw(sampled_from([0, 1]))
    )


@composite
def TypeVar(draw) -> ast.TypeVar:
    return ast.TypeVar(
        name=draw(name()),
        bound=draw(one_of(none(), expression()))
    )


@composite
def TypeVarTuple(draw) -> ast.TypeVarTuple:
    return ast.TypeVarTuple(name=draw(name()))


@composite
def ParamSpec(draw) -> ast.ParamSpec:
    return ast.ParamSpec(name=draw(name()))


@composite
def TypeAlias(draw) -> ast.TypeAlias:
    return ast.TypeAlias(
        name=draw(Name(ast.Store)),
        value=draw(expression()),
        type_params=draw(lists(one_of(TypeVar(), TypeVarTuple(), ParamSpec()), min_size=0, max_size=3))
    )


@composite
def FunctionDef(draw, statements) -> ast.FunctionDef:
    n = draw(name())
    args = draw(arguments())
    body = draw(lists(statements, min_size=1, max_size=3))
    decorator_list = draw(lists(Name(), min_size=0, max_size=2))
    type_params = draw(lists(one_of(TypeVar(), TypeVarTuple(), ParamSpec()), min_size=0, max_size=3))
    returns = draw(one_of(none(), expression()))
    return ast.FunctionDef(n, args, body, decorator_list, returns, type_params=type_params)


@composite
def AsyncFunctionDef(draw, statements) -> ast.AsyncFunctionDef:
    n = draw(name())
    args = draw(arguments())
    body = draw(lists(statements, min_size=1, max_size=3))
    decorator_list = draw(lists(Name(), min_size=0, max_size=2))
    type_params = draw(lists(one_of(TypeVar(), TypeVarTuple(), ParamSpec()), min_size=0, max_size=3))
    returns = draw(one_of(none(), expression()))
    return ast.AsyncFunctionDef(n, args, body, decorator_list, returns, type_params=type_params)


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

    # Remove duplicate keyword names
    seen_args = set()
    unique_keywords = []
    for kw in keywords:
        if kw.arg not in seen_args:
            seen_args.add(kw.arg)
            unique_keywords.append(kw)
    keywords = unique_keywords

    body = draw(lists(statements, min_size=1, max_size=3))
    decorator_list = draw(lists(Name(), min_size=0, max_size=2))
    return ast.ClassDef(
        name=n,
        bases=bases,
        keywords=keywords,
        body=body,
        decorator_list=decorator_list,
        type_params=draw(lists(one_of(TypeVar(), TypeVarTuple(), ParamSpec()), min_size=0, max_size=3))
    )


if hasattr(ast, 'Print'):
    simple_statements = one_of(
        Pass(),         # Simplest - no operation
        Break(),        # Simple control flow
        Continue(),
        Global(),       # Simple declarations
        Nonlocal(),
        Expr(),         # Expression statement
        Assign(),       # Simple assignments
        AugAssign(),
        AnnAssign(),    # Type annotations
        Print(),        # Python 2 print statement
        Assert(),       # More complex statements
        Raise(),
        Import(),       # Import statements
        ImportFrom()
        # Delete() - commented out
    )
else:
    simple_statements = one_of(
        Pass(),         # Simplest - no operation
        Break(),        # Simple control flow
        Continue(),
        Global(),       # Simple declarations
        Nonlocal(),
        Expr(),         # Expression statement
        Assign(),       # Simple assignments
        AugAssign(),
        AnnAssign(),    # Type annotations
        Assert(),       # More complex statements
        Raise(),
        Import(),       # Import statements
        ImportFrom(),
        TypeAlias()     # Most complex
    )


def suite() -> SearchStrategy:
    return recursive(
        simple_statements,
        lambda statements:
        one_of(
            If(statements),             # Simple conditional
            While(statements),          # Simple loop
            For(statements),            # Loop with iteration
            With(statements),           # Context manager
            FunctionDef(statements),    # Function definition
            AsyncFor(statements),       # Async variants
            AsyncWith(statements),
            AsyncFunctionDef(statements),
            Try(statements),            # Complex exception handling
            ClassDef(statements)        # Most complex
        ),
        max_leaves=100
    )


@composite
def Module(draw) -> ast.Module:
    b = draw(lists(suite(), min_size=1, max_size=3))
    return ast.Module(body=b, type_ignores=[])
