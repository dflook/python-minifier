"""
The is a backwards compatible shim for the ast module.

This is the best way to make the ast module work the same in both python 2 and 3.
This is essentially what the ast module was doing until 3.12, when it started throwing
deprecation warnings.
"""

from ast import *

# Ideally we don't import anything else

if 'TypeAlias' in globals():

    Constant.n = property(lambda self: self.value, lambda self, value: setattr(self, 'value', value))
    Constant.s = property(lambda self: self.value, lambda self, value: setattr(self, 'value', value))

    class Str(Constant):
        def __new__(cls, s, *args, **kwargs):
            return Constant(value=s, *args, **kwargs)

    class Bytes(Constant):
        def __new__(cls, s, *args, **kwargs):
            return Constant(value=s, *args, **kwargs)

    class Num(Constant):
        def __new__(cls, n, *args, **kwargs):
            return Constant(value=n, *args, **kwargs)

    class NameConstant(Constant):
        def __new__(cls, *args, **kwargs):
            return Constant(*args, **kwargs)

    class Ellipsis(Constant):
        def __new__(cls, *args, **kwargs):
            return Constant(value=literal_eval('...'), *args, **kwargs)