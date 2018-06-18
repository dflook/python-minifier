import ast
import copy


class QuoteDecider(ast.NodeVisitor):
    """
    Decides the quote style to use for f-strings

    Call a QuoteDecider object with the outer JoinedStr Node of an f-string expression.
    A list of up to four string elements is returned. This is a stack of the quote styles that
    should be used by the JoinedStr Nodes in the expression.

    Enclosed Str and Bytes Nodes may only use quote styles that have not been used by an outer JoinedStr.
    Note that Str and Bytes nodes may not contain a blackslash, so raw strings may be needed.
    The returned quote order accounts for this.

    """

    def __init__(self):
        super(QuoteDecider, self).__init__()

        self.nested = 0
        self.max_nested = 0

        self.special_chars = [[], [], [], []]

    def valid_quote(self, quote, start_level):
        for n_level in range(start_level, self.max_nested):
            if quote in self.special_chars[n_level]:
                return False

        return True

    def choose_level(self, level, candidates):
        if level == self.max_nested:
            return []

        for quote in candidates:
            if not self.valid_quote(quote, level):
                continue

            try:
                nested_candidates = copy.copy(candidates)
                nested_candidates.remove(quote)
                return [quote] + self.choose_level(level + 1, nested_candidates)
            except Exception:
                continue

        raise ValueError('Unable to find a quote style for nested f-string (level %i)' % level)

    def __call__(self, node):
        assert isinstance(node, ast.JoinedStr)

        # Assemble the list of special characters that need to be represented at each nesting level
        self.visit_JoinedStr(node)

        if self.max_nested > 4:
            raise ValueError('Impossible to represent that many nested strings')

        quote_order = self.choose_level(0, candidates=['"', "'", '"""', "'''"])

        return quote_order

    def visit_Str(self, node):
        assert isinstance(node, ast.Str)

        if '\\' in node.s:
            raise ValueError('Backslash not allowed in f-string expression')

        for special in ['"', "'", '\n']:
            if special in node.s:
                self.special_chars[self.nested].append(special)

        self.nested += 1
        self.max_nested = max(self.max_nested, self.nested)
        self.nested -= 1

    def visit_FormattedValue(self, node):
        assert isinstance(node, ast.FormattedValue)
        self.visit(node.value)

        if node.format_spec:
            self.visit_JoinedStr(node.format_spec)

    def visit_JoinedStr(self, node):
        assert isinstance(node, ast.JoinedStr)

        self.nested += 1
        self.max_nested = max(self.max_nested, self.nested)
        for v in node.values:
            if isinstance(v, ast.Str):
                continue
            self.visit(v)
        self.nested -= 1

    def visit_Bytes(self, node):
        assert isinstance(node, ast.Bytes)

        if '\\' in node.s:
            raise ValueError('Backslash not allowed in f-string expression')

        for special in ['"', "'", '\n']:
            if special in node.s:
                self.special_chars[self.nested].append(special)

        self.nested += 1
        self.max_nested = max(self.max_nested, self.nested)
        self.nested -= 1
