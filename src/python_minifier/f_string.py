"""
FString unparsing

This whole module feels like a hack.
Mostly because FStrings feel like a hack.

"""

import copy
import re

import python_minifier.ast_compat as ast

from python_minifier import UnstableMinification
from python_minifier.ast_compare import CompareError, compare_ast
from python_minifier.expression_printer import ExpressionPrinter
from python_minifier.ministring import MiniString
from python_minifier.token_printer import TokenTypes
from python_minifier.util import is_constant_node


class FString(object):
    """
    An F-string in the expression part of another f-string
    """

    def __init__(self, node, allowed_quotes, pep701):
        assert isinstance(node, ast.JoinedStr)

        self.node = node
        self.allowed_quotes = allowed_quotes
        self.pep701 = pep701

    def is_correct_ast(self, code):
        try:
            c = ast.parse(code, 'FString candidate', mode='eval')
            compare_ast(self.node, c.body)
            return True
        except Exception:
            return False

    def complete_debug_specifier(self, partial_specifier_candidates, value_node):
        assert isinstance(value_node, ast.FormattedValue)

        conversion = ''
        if value_node.conversion == 115:
            conversion = '!s'
        elif value_node.conversion == 114 and value_node.format_spec is not None:
            # This is the default for debug specifiers, unless there's a format_spec
            conversion = '!r'
        elif value_node.conversion == 97:
            conversion = '!a'

        conversion_candidates = [x + conversion for x in partial_specifier_candidates]

        if value_node.format_spec is not None:
            conversion_candidates = [c + ':' + fs for c in conversion_candidates for fs in FormatSpec(value_node.format_spec, self.allowed_quotes, self.pep701).candidates()]

        return [x + '}' for x in conversion_candidates]

    def candidates(self):
        actual_candidates = []

        for quote in self.allowed_quotes:
            candidates = ['']
            debug_specifier_candidates = []
            nested_allowed = copy.copy(self.allowed_quotes)

            if not self.pep701:
                nested_allowed.remove(quote)

            for v in self.node.values:
                if is_constant_node(v, ast.Str):

                    # Could this be used as a debug specifier?
                    if len(candidates) < 10:
                        debug_specifier = re.match(r'.*=\s*$', v.s)
                        if debug_specifier:
                            # Maybe!
                            try:
                                debug_specifier_candidates = [x + '{' + v.s for x in candidates]
                            except Exception:
                                continue

                    try:
                        candidates = [x + self.str_for(v.s, quote) for x in candidates]
                    except Exception:
                        continue
                elif isinstance(v, ast.FormattedValue):
                    try:
                        completed = self.complete_debug_specifier(debug_specifier_candidates, v)
                        candidates = [
                            x + y for x in candidates for y in FormattedValue(v, nested_allowed, self.pep701).get_candidates()
                        ] + completed
                        debug_specifier_candidates = []
                    except Exception:
                        continue
                else:
                    raise RuntimeError('Unexpected JoinedStr value')

                actual_candidates += ['f' + quote + x + quote for x in candidates]

        return filter(self.is_correct_ast, actual_candidates)

    def str_for(self, s, quote):
        return s.replace('{', '{{').replace('}', '}}')


class OuterFString(FString):
    """
    The outermost f-string

    Whereas the FString object assumes backslashes are disallowed, this
    OuterFString is free to use backslashes in the Str parts
    """

    def __init__(self, node, pep701=False):
        assert isinstance(node, ast.JoinedStr)
        super(OuterFString, self).__init__(node, ['"', "'", '"""', "'''"], pep701=pep701)

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
        mini_s = str(MiniString(s, quote)).replace('{', '{{').replace('}', '}}')

        if mini_s == '':
            return '\\\n'
        return mini_s


class FormattedValue(ExpressionPrinter):
    """
    An F-String Expression Part
    """

    def __init__(self, node, allowed_quotes, pep701):
        super(FormattedValue, self).__init__()

        assert isinstance(node, ast.FormattedValue)
        self.node = node
        self.allowed_quotes = allowed_quotes
        self.pep701 = pep701
        self.candidates = ['']

    def get_candidates(self):

        self.printer.delimiter('{')

        if self.is_curly(self.node.value):
            self.printer.delimiter(' ')

        self._expression(self.node.value)

        if self.node.conversion == 115:
            self.printer.append('!s', TokenTypes.Delimiter)
        elif self.node.conversion == 114:
            self.printer.append('!r', TokenTypes.Delimiter)
        elif self.node.conversion == 97:
            self.printer.append('!a', TokenTypes.Delimiter)

        if self.node.format_spec is not None:
            self.printer.delimiter(':')
            self._append(FormatSpec(self.node.format_spec, self.allowed_quotes, pep701=self.pep701).candidates())

        self.printer.delimiter('}')

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
        self.printer.append(str(Str(node.s, self.allowed_quotes, self.pep701)), TokenTypes.NonNumberLiteral)

    def visit_Bytes(self, node):
        self.printer.append(str(Bytes(node.s, self.allowed_quotes)), TokenTypes.NonNumberLiteral)

    def visit_JoinedStr(self, node):
        assert isinstance(node, ast.JoinedStr)
        if self.printer.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword, TokenTypes.SoftKeyword]:
            self.printer.delimiter(' ')
        self._append(FString(node, allowed_quotes=self.allowed_quotes, pep701=self.pep701).candidates())

    def visit_Lambda(self, node):
        self.printer.delimiter('(')
        super().visit_Lambda(node)
        self.printer.delimiter(')')

    def _finalize(self):
        self.candidates = [x + str(self.printer) for x in self.candidates]
        self.printer._code = ''

    def _append(self, candidates):
        self._finalize()
        self.candidates = [x + y for x in self.candidates for y in candidates]


class Str(object):
    """
    A Str node inside an f-string expression

    May use any of the allowed quotes. In Python <3.12, backslashes are not allowed.

    """

    def __init__(self, s, allowed_quotes, pep701=False):
        self._s = s
        self.allowed_quotes = allowed_quotes
        self.current_quote = None
        self.pep701 = pep701

    def _can_quote(self, c):
        if self.current_quote is None:
            return False

        if (c == '\n' or c == '\r') and len(self.current_quote) == 1 and not self.pep701:
            return False

        if c == self.current_quote[0]:
            return False

        return True

    def _get_quote(self, c):
        for quote in self.allowed_quotes:
            if not self.pep701 and (c == '\n' or c == '\r'):
                if len(quote) == 3:
                    return quote
            elif c != quote:
                return quote

        raise ValueError("Couldn't find a quote")

    def _literals(self):
        literal = ''
        for c in self._s:
            if not self._can_quote(c):
                if literal:
                    literal += self.current_quote
                    yield literal
                    literal = ''

                self.current_quote = self._get_quote(c)

            if literal == '':
                literal += self.current_quote

            if c == '\n':
                literal += '\\n'
            elif c == '\r':
                literal += '\\r'
            elif c == '\\':
                literal += '\\\\'
            else:
                literal += c

        if literal:
            literal += self.current_quote
            yield literal

    def __str__(self):
        if self._s == '':
            return str(min(self.allowed_quotes, key=len)) * 2

        if '\0' in self._s or ('\\' in self._s and not self.pep701):
            raise ValueError('Impossible to represent a character in f-string expression part')

        if not self.pep701 and ('\n' in self._s or '\r' in self._s):
            if '"""' not in self.allowed_quotes and "'''" not in self.allowed_quotes:
                raise ValueError(
                    'Impossible to represent newline character in f-string expression part without a long quote'
                )

        candidates = []
        for start_quote in self.allowed_quotes:
            self.current_quote = start_quote
            s = ''
            for literal in self._literals():
                if s and s[-1] == literal[0]:
                    s += ' '
                s += literal

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

    def __init__(self, node, allowed_quotes, pep701):
        assert isinstance(node, ast.JoinedStr)

        self.node = node
        self.allowed_quotes = allowed_quotes
        self.pep701 = pep701

    def candidates(self):

        candidates = ['']
        for v in self.node.values:
            if is_constant_node(v, ast.Str):
                candidates = [x + self.str_for(v.s) for x in candidates]
            elif isinstance(v, ast.FormattedValue):
                candidates = [
                    x + y for x in candidates for y in FormattedValue(v, self.allowed_quotes, self.pep701).get_candidates()
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

        raise ValueError("Couldn't find a quote")

    def _literals(self):
        literal = ''
        for b in self._b:
            if not self._can_quote(b):
                if literal:
                    literal += self.current_quote
                    yield literal
                    literal = ''

                self.current_quote = self._get_quote(b)

            if literal == '':
                literal = 'b' + self.current_quote
            literal += chr(b)

        if literal:
            literal += self.current_quote
            yield literal

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
            for literal in self._literals():
                if s and s[-1] == literal[0]:
                    s += ' '
                s += literal

            assert eval(s) == self._b
            candidates.append(s)

        return min(candidates, key=len)
