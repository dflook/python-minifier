import ast
import keyword
import string

from hypothesis import assume
from hypothesis.strategies import lists, sampled_from, recursive, text, composite, one_of, none

@composite
def name(draw):
    n = draw(text(alphabet=string.ascii_letters, min_size=1, max_size=3))

    assume(n not in keyword.kwlist)

    return n

@composite
def MatchValue(draw) -> ast.MatchValue:
    return ast.MatchValue(ast.Constant(0))

@composite
def MatchSingleton(draw) -> ast.MatchSingleton:
    return ast.MatchSingleton(draw(sampled_from([None, True, False])))

@composite
def MatchStar(draw) -> ast.MatchStar:
    return ast.MatchStar(draw(sampled_from([None, 'rest'])))

@composite
def MatchSequence(draw, pattern) -> ast.MatchSequence:
    l = draw(lists(pattern, min_size=1, max_size=3))
    return ast.MatchSequence(patterns=l)

@composite
def MatchMapping(draw, pattern) -> ast.MatchMapping:
    l = draw(lists(pattern, min_size=1, max_size=3))
    return ast.MatchMapping(keys=[ast.Num(0) for i in range(len(l))], patterns=l)

@composite
def MatchClass(draw, pattern) -> ast.MatchClass:
    patterns = draw(lists(pattern, min_size=0, max_size=3))

    kwd_patterns = draw(lists(pattern, min_size=0, max_size=3))
    kwd=['a' for i in range(len(kwd_patterns))]

    return ast.MatchClass(
        cls=ast.Name(draw(name()), ctx=ast.Load()),
        patterns=patterns,
        kwd_attrs=kwd,
        kwd_patterns=kwd_patterns
    )

@composite
def MatchAs(draw, pattern) -> ast.MatchAs:
    n = draw(none() | name())

    if n is None:
        p = None
    else:
        p = draw(pattern)

    return ast.MatchAs(pattern=p, name=n)

@composite
def MatchOr(draw, pattern) -> ast.MatchOr:
    l = draw(lists(pattern, min_size=2, max_size=3))
    return ast.MatchOr(patterns=l)

leaves = MatchValue() | MatchSingleton()

def pattern():
    return recursive(
        leaves,
        lambda pattern:
        one_of(
            MatchSequence(pattern),
            MatchMapping(pattern),
            MatchClass(pattern),
            MatchAs(pattern),
            MatchOr(pattern)
        ),
        max_leaves=150
    )

@composite
def Pattern(draw):
    """ A Match case pattern """
    return draw(pattern())
