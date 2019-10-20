import ast
import keyword
import math
import string
import unicodedata

from hypothesis import assume
from hypothesis._strategies import booleans
from hypothesis.searchstrategy import SearchStrategy
from hypothesis.strategies import integers, lists, binary, sampled_from, recursive, dictionaries
from hypothesis.strategies import text, composite, one_of, floats, complex_numbers, characters, none

comparison_operators = sampled_from([
    ast.Eq(),
    ast.NotEq(),
    ast.Lt(),
    ast.LtE(),
    ast.Gt(),
    ast.GtE(),
    ast.Is(),
    ast.IsNot(),
    ast.In(),
    ast.NotIn()
])

# region: Literals

@composite
def Num(draw) -> ast.AST:
    def to_node(n) -> ast.AST:
        if isinstance(n, int):
            return ast.Num(n) if n >= 0 else ast.UnaryOp(ast.USub(), ast.Num(abs(n)))
        elif isinstance(n, float):
            return ast.Num(n) if math.copysign(1.0, n) > 0.0 else ast.UnaryOp(ast.USub(), ast.Num(abs(n)))
        elif isinstance(n, complex):
            node = ast.parse(str(n), mode='eval')
            return node.body

        raise ValueError(n)

    return to_node(draw(integers() | floats(allow_nan=False) | complex_numbers(allow_infinity=True, allow_nan=False)))

@composite
def Str(draw) -> ast.Str:
    return ast.Str(''.join(draw(lists(characters(), min_size=0, max_size=3))))

@composite
def Bytes(draw) -> ast.Bytes:
    return ast.Bytes(draw(binary(max_size=3)))

@composite
def List(draw, expression) -> ast.List:
    l = draw(lists(expression, min_size=0, max_size=3))
    return ast.List(elts=l, ctx=ast.Load())

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
    return ast.Dict(keys=list(d.keys()), values=list(d.values()))

@composite
def NameConstant(draw) -> ast.NameConstant:
    return ast.NameConstant(draw(sampled_from([None, True, False])))

# endregion

@composite
def name(draw) -> SearchStrategy:
    other_id_start = [chr(i) for i in [0x1885, 0x1886, 0x2118, 0x212E, 0x309B, 0x309C]]
    other_id_continue = [chr(i) for i in [0x00B7, 0x0387, 0x19DA] + list(range(1369, 1371 + 1))]

    xid_start = draw(characters(whitelist_categories=['Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl'], whitelist_characters=['_'] + other_id_start, blacklist_characters=' '))
    xid_continue = draw(lists(characters(whitelist_categories=['Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl', 'Mn', 'Mc', 'Nd', 'Pc'], whitelist_characters=['_'] + other_id_start + other_id_continue, blacklist_characters=' '), min_size=0, max_size=2))

    n = xid_start + ''.join(xid_continue)

    normalised = unicodedata.normalize('NFKC', n)
    assume(normalised not in keyword.kwlist)
    assume(' ' not in normalised)
    try:
        ast.parse(normalised, mode='eval')
    except:
        assume(False)
    return normalised

@composite
def Name(draw, ctx=ast.Load) -> ast.Name:
    return ast.Name(draw(name()), ctx=ctx())

@composite
def UnaryOp(draw, expression) -> ast.UnaryOp:
    op = draw(sampled_from([ast.USub(), ast.UAdd(), ast.Not(), ast.Invert()]))
    l = draw(expression)
    return ast.UnaryOp(op, l)


@composite
def Compare(draw, expression) -> ast.Compare:
    num_comparators = draw(integers(min_value=2, max_value=3))

    return ast.Compare(left=draw(expression),
                       ops=[draw(comparison_operators) for i in range(num_comparators)],
                       comparators=[draw(expression) for i in range(num_comparators)])


@composite
def BinOp(draw, expression) -> ast.BinOp:
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

    le = draw(lists(expression, min_size=2, max_size=2))

    return ast.BinOp(le[0], op, le[1])


@composite
def BoolOp(draw, expression) -> ast.BoolOp:
    op = draw(sampled_from([
        ast.And(),
        ast.Or(),
    ]))

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
    attr = draw(text(alphabet=string.ascii_letters, min_size=1, max_size=3).filter(lambda n: n not in keyword.kwlist))
    return ast.Attribute(value, attr, ast.Load())


@composite
def Subscript(draw, expression) -> ast.Subscript:
    value = draw(expression)
    attr = draw(text(alphabet=string.ascii_letters, min_size=1, max_size=3))
    return ast.Subscript(value, attr, ast.Load())

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
    return ast.Index(draw(expression))

@composite
def Slice(draw, expression) -> ast.Slice:
    return ast.Slice(
        lower=draw(expression),
        upper=draw(expression),
        step=draw(expression)
    )

@composite
def ExtSlice(draw, expression) -> ast.ExtSlice:
    return ast.ExtSlice(
        draw(lists(
            Index(expression) | Slice(expression),
            min_size=2,
            max_size=4
        ))
    )

@composite
def Subscript(draw, expression, ctx=ast.Load) -> ast.Subscript:
    return ast.Subscript(
        value=draw(expression),
        slice=draw(Index(expression) | Slice(expression) | ExtSlice(expression)),
        ctx=ctx()
    )

@composite
def arg(draw, allow_annotation=True) -> ast.arg:

    if allow_annotation:
        annotation = draw(none() | expression())
    else:
        annotation = None

    return ast.arg(
        arg=draw(name()),
        annotation=annotation
    )

@composite
def arguments(draw, for_lambda=False) -> ast.arguments:

    allow_annotation = False if for_lambda else True

    args = draw(lists(arg(allow_annotation), max_size=2))
    kwonlyargs = draw(lists(arg(allow_annotation), max_size=2))
    vararg = draw(none() | arg(allow_annotation))
    kwarg = draw(none() | arg(allow_annotation))
    defaults=[]
    kw_defaults=draw(lists(none() | expression(), max_size=len(kwonlyargs), min_size=len(kwonlyargs)))
    return ast.arguments(
        args=args,
        vararg=vararg,
        kwonlyargs=kwonlyargs,
        kwarg=kwarg,
        defaults=defaults,
        kw_defaults=kw_defaults
    )

@composite
def Lambda(draw, expression) -> ast.Lambda:
    return ast.Lambda(args=draw(arguments(for_lambda=True)),
                      body=draw(expression))

@composite
def comprehension(draw, expression) -> ast.comprehension:
    return ast.comprehension(
        target=draw(Name(ast.Store)),
        iter=draw(expression),
        ifs=draw(lists(expression, min_size=0, max_size=3)),
        is_async=draw(booleans())
    )

@composite
def ListComp(draw, expression) -> ast.ListComp:
    return ast.ListComp(
        elt=draw(expression),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )

@composite
def SetComp(draw, expression) -> ast.SetComp:
    return ast.SetComp(
        elt=draw(expression),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )

@composite
def GeneratorExp(draw, expression) -> ast.GeneratorExp:
    return ast.GeneratorExp(
        elt=draw(expression),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )

@composite
def DictComp(draw, expression) -> ast.DictComp:
    return ast.DictComp(
        key=draw(expression),
        value=draw(expression),
        generators=draw(lists(comprehension(expression), min_size=1, max_size=3))
    )

leaves = NameConstant() | \
        Name() | \
        Num() | \
        Str() | \
        Bytes()

def expression() -> SearchStrategy:
    return recursive(
        leaves,
        lambda expression:
        one_of(
            Yield(expression),
            YieldFrom(expression),
            Await(expression),
            IfExp(expression),
            Call(expression),
            BinOp(expression),
            Set(expression),
            List(expression),
            Tuple(expression),
            BoolOp(expression),
            UnaryOp(expression),
            Attribute(expression),
            Dict(expression),
            Compare(expression),
            Lambda(expression),
            ListComp(expression),
            GeneratorExp(expression),
            DictComp(expression),
            Subscript(expression)
        ),
        max_leaves=150
    )

@composite
def Expression(draw) -> ast.Expression:
    """ An eval expression """
    e = draw(expression())
    return ast.Expression(e)
