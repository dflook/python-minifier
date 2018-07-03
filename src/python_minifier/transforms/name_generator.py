import string
import itertools
import keyword

def name_generator():

    valid_first = string.ascii_uppercase + '_' + string.ascii_lowercase
    valid_rest = string.digits + valid_first

    for c in valid_first:
        yield c

    for length in itertools.count(1):
        for first in valid_first:
            for rest in itertools.product(valid_rest, repeat=length):
                name = first
                name += ''.join(rest)
                yield name

def name_filter(predefined=None):
    """
    Yield all valid python identifiers

    Name are returned sorted by length, then string sort order.

    Names that already have meaning in python (keywords and builtins)
    will not be included in the output.
    Names in predefined will also not be included in the output.

    :param predefined: Predefined names that will not be returned
    :type predefined: list[str]
    :rtype: Iterable[str]

    """

    try:
        import builtins
    except ImportError:
        import __builtin__ as builtins

    reserved = keyword.kwlist + dir(builtins)

    if predefined:
        reserved += predefined

    for name in name_generator():
        if name not in reserved:
            yield name
