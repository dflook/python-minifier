"""Tools for assembling python code from tokens."""

import re
import sys


class TokenTypes(object):
    NoToken = 0
    Identifier = 1
    Keyword = 2
    SoftKeyword = 3
    NumberLiteral = 4
    NonNumberLiteral = 5
    Delimiter = 6
    Operator = 7
    NewLine = 8
    EndStatement = 9

class Delimiter(object):
    def __init__(self, terminal_printer, delimiter=',', group_chars=None):  # type: (TerminalPrinter, str, tuple[str, str]) -> None
        self._terminal_printer = terminal_printer
        self._delimiter = delimiter

        if group_chars:
            self._start_char, self._end_char = group_chars

        self.first = True

        self._context_manager = False

    def __enter__(self):  # type: () -> Delimiter
        self._context_manager = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.first and self._end_char:
            self._terminal_printer.delimiter(self._end_char)

    def new_item(self):  # type: () -> None
        if self.first:
            self.first = False
            if self._context_manager and self._start_char:
                self._terminal_printer.delimiter(self._start_char)
        else:
            self._terminal_printer.delimiter(self._delimiter)

class TerminalPrinter(object):
    """
    Concatenates terminal symbols of the python grammar
    """

    __slots__ = ['__code', 'indent', 'unicode_literals', 'previous_token', '_prefer_single_line', '_allow_invalid_num_warnings']

    def __init__(self, prefer_single_line=False, allow_invalid_num_warnings=False):  # type: (bool, bool) -> None
        """
        :param prefer_single_line: If True, chooses to put as much code as possible on a single line.
        :param allow_invalid_num_warnings: If True, allows invalid number literals to be printe that may cause warnings.
        """

        self._prefer_single_line = prefer_single_line
        self._allow_invalid_num_warnings = allow_invalid_num_warnings

        self.__code = ''
        self.indent = TokenTypes.NoToken  # type: int
        self.unicode_literals = False
        self.previous_token = 0  # type: int

    def __str__(self):  # type: () -> str
        return self.__code

    def identifier(self, name):  # type: (str) -> None
        assert isinstance(name, str)

        if self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword, TokenTypes.SoftKeyword, TokenTypes.NumberLiteral]:
            self.delimiter(' ')

        self.__code += name
        self.previous_token = TokenTypes.Identifier

    def keyword(self, kw):  # type: (str) -> None
        assert kw in [
            'False', 'None', 'True', 'and', 'as',
            'assert', 'async', 'await', 'break',
            'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'finally',
            'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'nonlocal', 'not',
            'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield', '_', 'case', 'match'
        ]

        if self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword, TokenTypes.SoftKeyword, TokenTypes.NumberLiteral]:
            self.delimiter(' ')

        self.__code += kw

        if kw in ['_', 'case', 'match']:
            self.previous_token = TokenTypes.SoftKeyword
        else:
            self.previous_token = TokenTypes.Keyword

    def stringliteral(self, value):  # type: (AnyStr) -> None
        s = repr(value)

        if sys.version_info < (3, 0) and self.unicode_literals:
            if s[0] == 'u':
                # Remove the u prefix since literals are unicode by default
                s = s[1:]
            else:
                # Add a b prefix to indicate it is NOT unicode
                s = 'b' + s

        if len(s) > 0 and s[0].isalpha() and self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword, TokenTypes.SoftKeyword]:
            self.delimiter(' ')

        self.__code += s
        self.previous_token = TokenTypes.NonNumberLiteral

    def bytesliteral(self, value):  # type: (bytes) -> None
        s = repr(value)

        if len(s) > 0 and s[0].isalpha() and self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword, TokenTypes.SoftKeyword]:
            self.delimiter(' ')

        self.__code += s
        self.previous_token = TokenTypes.NonNumberLiteral

    def fstring(self, s):  # type: (str) -> None
        assert isinstance(s, str)

        if self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword, TokenTypes.SoftKeyword]:
            self.delimiter(' ')

        self.__code += s
        self.previous_token = TokenTypes.NonNumberLiteral

    def delimiter(self, d):  # type: (str) -> None
        assert d in [
            '(', ')', '[', ']', '{', '}', ' ',
            ',', ':', '.', ';', '@', '=', '->',
            '+=', '-=', '*=', '/=', '//=', '%=', '@=',
            '&=', '|=', '^=', '>>=', '<<=', '**=', '|'
        ]

        self.__code += d
        self.previous_token = TokenTypes.Delimiter

    def operator(self, o):  # type: (str) -> None
        assert o in [
            '+', '-', '*', '**', '/', '//', '%', '@',
            '<<', '>>', '&', '|', '^', '~', ':=',
            '<', '>', '<=', '>=', '==', '!='
        ]

        self.__code += o
        self.previous_token = TokenTypes.Operator

    def integer(self, v):  # type: (int) -> None
        assert isinstance(v, int)

        s = repr(v)
        h = hex(v)

        if self.previous_token == TokenTypes.SoftKeyword:
            self.delimiter(' ')
        elif self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword]:
            self.delimiter(' ')

        self.__code += h if len(h) < len(s) else s

        self.previous_token = TokenTypes.NumberLiteral

    def imagnumber(self, value):  # type: (complex) -> None
        assert isinstance(value, complex)

        s = repr(value)

        if s in ['infj', 'inf*j']:
            s = '1e999j'
        elif s in ['-infj', '-inf*j']:
            s = '-1e999j'

        if self.previous_token == TokenTypes.SoftKeyword:
            self.delimiter(' ')
        elif self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword]:
            self.delimiter(' ')

        self.__code += s

        self.previous_token = TokenTypes.NumberLiteral

    def floatnumber(self, v):  # type: (float) -> None
        assert isinstance(v, float)

        s = repr(v)

        s = s.replace('e+', 'e')

        add_e = re.match(r'^(\d+?)(0+).0$', s)
        if add_e:
            s = add_e.group(1) + 'e' + str(len(add_e.group(2)))

        if s == 'inf':
            s = '1e999'
        elif s == '-inf':
            s = '-1e999'
        elif s.startswith('0.'):
            s = s[1:]
        elif s.startswith('-0.'):
            s = '-' + s[2:]
        elif s.endswith('.0'):
            s = s[:-1]

        if self.previous_token == TokenTypes.SoftKeyword:
            self.delimiter(' ')
        elif self.previous_token in [TokenTypes.Identifier, TokenTypes.Keyword]:
            self.delimiter(' ')

        self.__code += s

        self.previous_token = TokenTypes.NumberLiteral

    def newline(self):  # type: () -> None
        if self.__code == '':
            return

        self.__code = self.__code.rstrip('\n\t;')
        self.__code += '\n'
        self.__code += '\t' * self.indent

        self.previous_token = TokenTypes.NewLine

    def enter_block(self):  # type: () -> None
        self.indent += 1
        self.newline()

    def leave_block(self):  # type: () -> None
        self.indent -= 1
        self.newline()

    def end_statement(self):  # type: () -> None
        """ End a statement with a newline, or a semi-colon if it saves characters. """

        if self.indent == 0:
            self.newline()
        else:
            if self.__code[-1] != ';':
                self.__code += ';'

        self.previous_token = TokenTypes.EndStatement

    def append(self, code):
        self.__code += code
