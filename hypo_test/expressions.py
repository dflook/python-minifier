import python_minifier.ast_compat as ast
import keyword
import math
import string
import unicodedata

from hypothesis import assume
from hypothesis.strategies import (
    SearchStrategy,
    binary,
    booleans,
    characters,
    complex_numbers,
    composite,
    dictionaries,
    floats,
    integers,
    lists,
    none,
    one_of,
    recursive,
    sampled_from,
    text
)

comparison_operators = sampled_from(
    [
        ast.Eq(),      # Most common comparison
        ast.NotEq(),
        ast.Lt(),      # Simple ordering
        ast.Gt(),
        ast.LtE(),
        ast.GtE(),
        ast.In(),      # Membership tests
        ast.NotIn(),
        ast.Is(),      # Identity tests (less common)
        ast.IsNot()
    ]
)


# region: Literals

@composite
def Num(draw) -> ast.AST:
    def to_node(n) -> ast.AST:
        if isinstance(n, int):
            return ast.Constant(value=n) if n >= 0 else ast.UnaryOp(ast.USub(), ast.Constant(value=abs(n)))
        elif isinstance(n, float):
            return ast.Constant(value=n) if math.copysign(1.0, n) > 0.0 else ast.UnaryOp(ast.USub(), ast.Constant(value=abs(n)))
        elif isinstance(n, complex):
            node = ast.parse(str(n), mode='eval')
            return node.body

        raise ValueError(n)

    return to_node(draw(one_of(
        integers(),  # Shrinks to 0
        floats(allow_nan=False),  # Shrinks to 0.0
        complex_numbers(allow_infinity=True, allow_nan=False)  # Most complex
    )))


@composite
def Str(draw) -> ast.Constant:
    # Choose between simple and complex strings for better shrinking
    use_simple = draw(booleans())

    if use_simple:
        # Simple ASCII strings that shrink well
        s = draw(text(string.ascii_letters + string.digits + ' ', min_size=0, max_size=3))
    else:
        # Complex unicode for thorough testing
        # Only filter out surrogates which are invalid in Python strings
        safe_chars = characters(
            blacklist_categories=['Cs'],  # No surrogates
            max_codepoint=0xFFFF          # Stay within BMP for simplicity
        )
        s = ''.join(draw(lists(safe_chars, min_size=0, max_size=3)))

    return ast.Constant(value=s)


@composite
def Bytes(draw) -> ast.Constant:
    return ast.Constant(value=draw(binary(max_size=3)))


@composite
def List(draw, expression) -> ast.List:
    elements = draw(lists(expression, min_size=0, max_size=3))
    return ast.List(elts=elements, ctx=ast.Load())


@composite
def Tuple(draw, expression) -> ast.Tuple:
    t = draw(lists(expression, min_size=0, max_size=3))
    return ast.Tuple(elts=t, ctx=ast.Load())


@composite
def Set(draw, expression) -> ast.Set:
    s = draw(lists(expression, min_size=1, max_size=3))
    return ast.Set(elts=s)


@composite
def Dict(draw, expression) -> ast.Dict:
    d = draw(dictionaries(expression, expression, min_size=0, max_size=3))
    items = list(d.items())  # Get items as pairs to maintain key-value relationships
    return ast.Dict(keys=[k for k, v in items], values=[v for k, v in items])


@composite
def NameConstant(draw) -> ast.Constant:
    return ast.Constant(value=draw(sampled_from([None, False, True])))


# endregion

@composite
def name(draw) -> SearchStrategy:
    # Choose between simple and complex, but in a way that shrinks to simple
    use_unicode = draw(booleans())

    if not use_unicode:
        # Simple ASCII names (will be the shrunk case)
        first = draw(sampled_from(string.ascii_letters + '_'))
        rest = draw(text(string.ascii_letters + string.digits + '_', min_size=0, max_size=2))
        n = first + rest
    else:
        # Complex unicode names (for thorough testing)
        other_id_start = [chr(i) for i in [0x1885, 0x1886, 0x2118, 0x212E, 0x309B, 0x309C]]
        other_id_continue = [chr(i) for i in [0x00B7, 0x0387, 0x19DA] + list(range(1369, 1371 + 1))]

        xid_start = draw(characters(whitelist_categories=['Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl'],
                                    whitelist_characters=['_'] + other_id_start,
                                    blacklist_characters=' '))
        xid_continue = draw(
            lists(
                characters(whitelist_categories=['Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl', 'Mn', 'Mc', 'Nd', 'Pc'],
                          whitelist_characters=['_'] + other_id_start + other_id_continue,
                          blacklist_characters=' '),
                min_size=0,
                max_size=2
            )
        )
        n = xid_start + ''.join(xid_continue)
        n = unicodedata.normalize('NFKC', n)

    # Handle keywords by prefixing with underscore
    if n in keyword.kwlist:
        return '_' + n

    # Validate it's a proper identifier
    if not n.isidentifier():
        # Shouldn't happen with our generation, but just in case
        assume(False)

    return n


@composite
def Name(draw, ctx=ast.Load) -> ast.Name:
    return ast.Name(draw(name()), ctx=ctx())


@composite
def UnaryOp(draw, expression) -> ast.UnaryOp:
    op = draw(sampled_from([ast.UAdd(), ast.USub(), ast.Not(), ast.Invert()]))
    operand = draw(expression)
    return ast.UnaryOp(op, operand)


@composite
def Compare(draw, expression) -> ast.Compare:
    num_comparators = draw(integers(min_value=2, max_value=3))

    return ast.Compare(
        left=draw(expression),
        ops=[draw(comparison_operators) for i in range(num_comparators)],
        comparators=[draw(expression) for i in range(num_comparators)]
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
def BoolOp(draw, expression) -> ast.BoolOp:
    op = draw(
        sampled_from(
            [
                ast.And(),
                ast.Or(),
            ]
        )
    )

    le = draw(lists(expression, min_size=2, max_size=3))
    return ast.BoolOp(op, values=le)


@composite
def Call(draw, expression) -> ast.Call:
    func = draw(expression)
    args = draw(lists(expression, min_size=1, max_size=3))
    keywords = []
    return ast.Call(func, args, keywords)


@composite
def IfExp(draw, expression) -> ast.IfExp:
    test = draw(expression)
    body = draw(expression)
    orelse = draw(expression)
    return ast.IfExp(test, body, orelse)


@composite
def Attribute(draw, expression) -> ast.Attribute:
    value = draw(expression)
    # Use our improved name strategy for attributes too
    attr = draw(name())
    return ast.Attribute(value, attr, ast.Load())

@composite
def Yield(draw, expression) -> ast.Yield:
    return ast.Yield(draw(expression))


@composite
def YieldFrom(draw, expression) -> ast.YieldFrom:
    return ast.YieldFrom(draw(expression))


@composite
def Await(draw, expression) -> ast.Await:
    return ast.Await(draw(expression))


@composite
def Index(draw, expression) -> ast.Index:
    return ast.Index(draw(one_of(Ellipsis(), expression)))


@composite
def Slice(draw, expression) -> ast.Slice:
    return ast.Slice(
        lower=draw(expression),
        upper=draw(expression),
        step=draw(one_of(none(), expression))
    )


@composite
def Ellipsis(draw) -> ast.Constant:
    return ast.Constant(value=...)


@composite
def ExtSlice(draw, expression) -> ast.ExtSlice:
    slice = draw(Slice(expression))

    return ast.ExtSlice(
        [slice] +
        draw(
            lists(
                Index(expression) | Slice(expression),
                min_size=1,
                max_size=3
            )
        )
    )


@composite
def Subscript(draw, expression, ctx=ast.Load) -> ast.Subscript:
    return ast.Subscript(
        value=draw(expression),
        slice=draw(one_of(Index(expression), Slice(expression), ExtSlice(expression))),
        ctx=ctx()
    )


@composite
def arg(draw, allow_annotation=True) -> ast.arg:

    if allow_annotation:
        annotation = draw(one_of(none(), expression()))
    else:
        annotation = None

    return ast.arg(
        arg=draw(name()),
        annotation=annotation
    )


@composite
def arguments(draw, for_lambda=False) -> ast.arguments:

    allow_annotation = not for_lambda

    args = draw(lists(arg(allow_annotation), max_size=2))
    posonlyargs = draw(lists(arg(allow_annotation), max_size=2))
    kwonlyargs = draw(lists(arg(allow_annotation), max_size=2))
    vararg = draw(one_of(none(), arg(allow_annotation)))
    kwarg = draw(one_of(none(), arg(allow_annotation)))
    defaults = []
    kw_defaults = draw(lists(one_of(none(), expression()), max_size=len(kwonlyargs), min_size=len(kwonlyargs)))
    return ast.arguments(
        posonlyargs=posonlyargs,
        args=args,
        vararg=vararg,
        kwonlyargs=kwonlyargs,
        kwarg=kwarg,
        defaults=defaults,
        kw_defaults=kw_defaults
    )


@composite
def Lambda(draw, expression) -> ast.Lambda:
    return ast.Lambda(
        args=draw(arguments(for_lambda=True)),
        body=draw(expression)
    )


@composite
def comprehension(draw, expression) -> ast.comprehension:
    return ast.comprehension(
        target=draw(Name(ast.Store)),
        iter=draw(expression),
        ifs=draw(lists(expression, min_size=0, max_size=3)),
        is_async=draw(booleans())
    )


@composite
def comprehension_element(draw, expression):
    """
    The element of a list, set or generator comprehension

    PEP 798 (Python 3.15) allows this to be unpacked with `*`, as in
    `[*L for L in lists]`. That reuses Starred in the existing `elt` slot rather
    than adding a field, so it is invisible to a diff of node `_fields`.
    """

    element = draw(expression)
    if draw(booleans()):
        return ast.Starred(value=element, ctx=ast.Load())
    return element


@composite
def ListComp(draw, expression) -> ast.ListComp:
    return ast.ListComp(
        elt=draw(comprehension_element(expression)),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )


@composite
def SetComp(draw, expression) -> ast.SetComp:
    return ast.SetComp(
        elt=draw(comprehension_element(expression)),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )


@composite
def GeneratorExp(draw, expression) -> ast.GeneratorExp:
    return ast.GeneratorExp(
        elt=draw(comprehension_element(expression)),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )


@composite
def DictComp(draw, expression) -> ast.DictComp:
    # PEP 798 (Python 3.15) `{**d for d in dicts}` is a DictComp whose value is
    # None, with the unpacked expression in key.
    unpacked = draw(booleans())
    return ast.DictComp(
        key=draw(expression),
        value=None if unpacked else draw(expression),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )


leaves = one_of(
    NameConstant(),
    Name(),
    Num(),
    Str(),
    Bytes()
)


# Group related operations for better recursive structure
def binary_operations(expr):
    """Simple binary and comparison operations"""
    return one_of(
        BinOp(expr),
        Compare(expr),
        BoolOp(expr),
        UnaryOp(expr)
    )

def collections(expr):
    """Collection types"""
    return one_of(
        List(expr),
        Tuple(expr),
        Set(expr),
        Dict(expr)
    )

def calls_and_access(expr):
    """Function calls and member access"""
    return one_of(
        Call(expr),
        Attribute(expr),
        Subscript(expr)
    )

def control_flow(expr):
    """Control flow expressions"""
    return one_of(
        IfExp(expr),
        Yield(expr),
        YieldFrom(expr)
    )

def comprehensions(expr):
    """List/dict/generator comprehensions"""
    return one_of(
        ListComp(expr),
        DictComp(expr),
        GeneratorExp(expr)
    )


def async_expression() -> SearchStrategy:
    return recursive(
        leaves,
        lambda expression: one_of(
            binary_operations(expression),
            collections(expression),
            calls_and_access(expression),
            control_flow(expression),
            comprehensions(expression),
            Await(expression),  # Async-specific
            Lambda(expression)   # Complex case
        ),
        max_leaves=50
    )


def expression() -> SearchStrategy:
    return recursive(
        leaves,
        lambda expression: one_of(
            binary_operations(expression),
            collections(expression),
            calls_and_access(expression),
            control_flow(expression),
            comprehensions(expression),
            Lambda(expression)   # Complex case
        ),
        max_leaves=50
    )


@composite
def Expression(draw) -> ast.Expression:
    """ An eval expression """
    e = draw(expression())
    return ast.Expression(e)
