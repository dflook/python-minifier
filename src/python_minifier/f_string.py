"""
FString unparsing

This whole module feels like a hack.
Mostly because FStrings feel like a hack.

"""

import ast
import copy

from python_minifier import UnstableMinification
from python_minifier.ast_compare import CompareError
from python_minifier.ast_compare import compare_ast
from python_minifier.expression_printer import ExpressionPrinter
from python_minifier.ministring import MiniString
from python_minifier.rename.util import is_str


class FString(object):
    """
    An F-string in the expression part of another f-string
    """

    def __init__(self, node, allowed_quotes):
        assert isinstance(node, ast.JoinedStr)

        self.node = node
        self.allowed_quotes = allowed_quotes

    def is_correct_ast(self, code):
        try:
            c = ast.parse(code, 'FString candidate', mode='eval')
            compare_ast(self.node, c.body)
            return True
        except Exception as e:
            return False

    def candidates(self):
        actual_candidates = []

        for quote in self.allowed_quotes:
            candidates = ['']
            nested_allowed = copy.copy(self.allowed_quotes)
            nested_allowed.remove(quote)
            for v in self.node.values:
                if is_str(v):
                    try:
                        candidates = [x + self.str_for(v.s, quote) for x in candidates]
                    except Exception as e:
                        continue
                elif isinstance(v, ast.FormattedValue):
                    try:
                        candidates = [
                            x + y for x in candidates for y in FormattedValue(v, nested_allowed).get_candidates()
                        ]
                    except Exception as e:
                        continue
                else:
                    raise RuntimeError('Unexpected JoinedStr value')

                actual_candidates += ['f' + quote + x + quote for x in candidates]

        actual_candidates = filter(self.is_correct_ast, actual_candidates)
        return actual_candidates

    def str_for(self, s, quote):
        return s.replace('{', '{{').replace('}', '}}')


class OuterFString(FString):
    """
    The outermost f-string

    Whereas the FString object assumes backslashes are disallowed, this
    OuterFString is free to use backslashes in the Str parts
    """

    def __init__(self, node):
        assert isinstance(node, ast.JoinedStr)
        super(OuterFString, self).__init__(node, ['"', "'", '"""', "'''"])

    def __str__(self):
        if len(self.node.values) == 0:
            return 'f' + min(self.allowed_quotes, key=len) * 2

        candidates = list(self.candidates())

        for candidate in candidates:

            try:
                minified_f_string = ast.parse(candidate, 'python_minifier.f_string output', mode='eval').body
            except SyntaxError as syntax_error:
                raise UnstableMinification(syntax_error, '', candidate)

            try:
                compare_ast(self.node, minified_f_string)
            except CompareError as compare_error:
                raise UnstableMinification(compare_error, '', candidate)

        if not candidates:
            raise ValueError('Unable to create representation for f-string')

        return min(candidates, key=len)

    def str_for(self, s, quote):
        return str(MiniString(s, quote)).replace('{', '{{').replace('}', '}}')


class FormattedValue(ExpressionPrinter):
    """
    An F-String Expression Part
    """

    def __init__(self, node, allowed_quotes):
        super(FormattedValue, self).__init__()

        assert isinstance(node, ast.FormattedValue)
        self.node = node
        self.allowed_quotes = allowed_quotes
        self.candidates = ['']

    def get_candidates(self):

        self.code = '{'

        if self.is_curly(self.node.value):
            self.code += ' '

        self._expression(self.node.value)

        if self.node.conversion == 115:
            self.code += '!s'
        elif self.node.conversion == 114:
            self.code += '!r'
        elif self.node.conversion == 97:
            self.code += '!a'

        if self.node.format_spec is not None:
            self.code += ':'
            self._append(FormatSpec(self.node.format_spec, self.allowed_quotes).candidates())

        self.code += '}'

        self._finalize()
        return self.candidates

    def is_curly(self, node):
        if isinstance(node, (ast.SetComp, ast.DictComp, ast.Set, ast.Dict)):
            return True

        if isinstance(node, (ast.Expr, ast.Attribute, ast.Subscript)):
            return self.is_curly(node.value)

        if isinstance(node, (ast.Compare, ast.BinOp)):
            return self.is_curly(node.left)

        if isinstance(node, ast.Call):
            return self.is_curly(node.func)

        if isinstance(node, ast.BoolOp):
            return self.is_curly(node.values[0])

        if isinstance(node, ast.IfExp):
            return self.is_curly(node.body)

        return False

    def visit_Str(self, node):
        self.code += str(Str(node.s, self.allowed_quotes))

    def visit_Bytes(self, node):
        self.code += str(Bytes(node.s, self.allowed_quotes))

    def visit_JoinedStr(self, node):
        assert isinstance(node, ast.JoinedStr)
        self.token_break()
        self._append(FString(node, allowed_quotes=self.allowed_quotes).candidates())

    def _finalize(self):
        self.candidates = [x + self.code for x in self.candidates]
        self.code = ''

    def _append(self, candidates):
        self._finalize()
        self.candidates = [x + y for x in self.candidates for y in candidates]


class Str(object):
    """
    A Str node inside an f-string expression

    May use any of the allowed quotes, no backslashes!

    """

    def __init__(self, s, allowed_quotes):
        self._s = s
        self.allowed_quotes = allowed_quotes
        self.current_quote = None

    def _can_quote(self, c):
        if self.current_quote is None:
            return False

        if (c == '\n' or c == '\r') and len(self.current_quote) == 1:
            return False

        if c == self.current_quote[0]:
            return False

        return True

    def _get_quote(self, c):
        for quote in self.allowed_quotes:
            if c == '\n' or c == '\r':
                if len(quote) == 3:
                    return quote
            elif c != quote:
                return quote

        raise ValueError('Couldn\'t find a quote')

    def _literals(self):
        l = ''
        for c in self._s:
            if not self._can_quote(c):
                if l:
                    l += self.current_quote
                    yield l
                    l = ''

                self.current_quote = self._get_quote(c)

            if l == '':
                l += self.current_quote
            l += c

        if l:
            l += self.current_quote
            yield l

    def __str__(self):
        if self._s == '':
            return str(min(self.allowed_quotes, key=len)) * 2

        if '\0' in self._s or '\\' in self._s:
            raise ValueError('Impossible to represent a %r character in f-string expression part')

        if '\n' in self._s or '\r' in self._s:
            if '"""' not in self.allowed_quotes and "'''" not in self.allowed_quotes:
                raise ValueError(
                    'Impossible to represent newline character in f-string expression part without a long quote'
                )

        candidates = []
        for start_quote in self.allowed_quotes:
            self.current_quote = start_quote
            s = ''
            for l in self._literals():
                if s and s[-1] == l[0]:
                    s += ' '
                s += l

            if eval(s) == self._s:
                candidates.append(s)

        if candidates:
            return min(candidates, key=len)
        else:
            raise ValueError('Unable to string')


class FormatSpec(object):
    """
    A FormattedValue format spec

    The AST looks like another f-string. This time there are no quotes.

    """

    def __init__(self, node, allowed_quotes):
        assert isinstance(node, ast.JoinedStr)

        self.node = node
        self.allowed_quotes = allowed_quotes

    def candidates(self):

        candidates = ['']
        for v in self.node.values:
            if is_str(v):
                candidates = [x + self.str_for(v.s) for x in candidates]
            elif isinstance(v, ast.FormattedValue):
                candidates = [
                    x + y for x in candidates for y in FormattedValue(v, self.allowed_quotes).get_candidates()
                ]
            else:
                raise RuntimeError('Unexpected JoinedStr value')

        return candidates

    def str_for(self, s):
        return s.replace('{', '{{').replace('}', '}}')


class Bytes(object):
    """
    A Bytes node inside an f-string expression

    May use any of the allowed quotes, no backslashes!

    """

    def __init__(self, b, allowed_quotes):
        self._b = b
        self.allowed_quotes = allowed_quotes
        self.current_quote = None

    def _can_quote(self, c):
        if self.current_quote is None:
            return False

        if (c == ord(b'\n') or c == ord(b'\r')) and len(self.current_quote) == 1:
            return False

        if chr(c) == self.current_quote[0]:
            return False

        return True

    def _get_quote(self, c):
        for quote in self.allowed_quotes:
            if c == ord(b'\n') or c == ord(b'\r'):
                if len(quote) == 3:
                    return quote
            elif chr(c) != quote:
                return quote

        raise ValueError('Couldn\'t find a quote')

    def _literals(self):
        l = ''
        for b in self._b:
            if not self._can_quote(b):
                if l:
                    l += self.current_quote
                    yield l
                    l = ''

                self.current_quote = self._get_quote(b)

            if l == '':
                l = 'b' + self.current_quote
            l += chr(b)

        if l:
            l += self.current_quote
            yield l

    def __str__(self):
        if self._b == b'':
            return 'b' + str(min(self.allowed_quotes, key=len)) * 2

        if b'\0' in self._b or b'\\' in self._b:
            raise ValueError('Impossible to represent a %r character in f-string expression part')

        if b'\n' in self._b or b'\r' in self._b:
            if '"""' not in self.allowed_quotes and "'''" not in self.allowed_quotes:
                raise ValueError(
                    'Impossible to represent newline character in f-string expression part without a long quote'
                )

        candidates = []
        for start_quote in self.allowed_quotes:
            self.current_quote = start_quote
            s = ''
            for l in self._literals():
                if s and s[-1] == l[0]:
                    s += ' '
                s += l

            assert eval(s) == self._b
            candidates.append(s)

        return min(candidates, key=len)
