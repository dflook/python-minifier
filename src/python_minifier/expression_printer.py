import ast
import sys


class ExpressionPrinter(object):
    """
    Builds the smallest possible exact representation of an ast
    """

    def __init__(self):

        self.code = ''
        self.indent = 0
        self.unicode_literals = False

        self.precedences = {
            'Lambda': 2,
            'IfExp': 3,
            'comprehension': 3.5,
            'Or': 4,
            'And': 5,
            'Not': 6,
            'In': 7, 'NotIn': 7, 'Is': 7, 'IsNot': 7, 'Lt': 7, 'LtE': 7, 'Gt': 7, 'GtE': 7, 'NotEq': 7, 'Eq': 7,
            'BitOr': 8,
            'BitXor': 9,
            'BitAnd': 10,
            'LShift': 11, 'RShift': 11,
            'Add': 12, 'Sub': 12,
            'Mult': 13, 'Div': 13, 'FloorDiv': 13, 'Mod': 13, 'MatMult': 13,
            'UAdd': 14, 'USub': 14, 'Invert': 14,
            'Pow': 15,
            'Await': 16,
            'Subscript': 17, 'Call': 17, 'Attribute': 17,
            'Tuple': 18, 'Set': 18, 'List': 18, 'Dict': 18,
        }

    def __call__(self, module):
        """
        Generate the source code for an AST

        :param module: The Module to generate code for
        :type module: ast.Module
        :rtype: str

        """

        self.visit(module)
        return self.code

    def precedence(self, node):
        """
        The precedence of an expression

        Node will usually be an operator or literal.
        Nodes with no precedence value return 0.

        :param node: The AST node to decide precedence for
        :type node: ast.Node
        :rtype: int

        """

        if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp)):
            return self.precedences[node.op.__class__.__name__]
        elif isinstance(node, ast.Compare):
            return min(self.precedences[n.__class__.__name__] for n in node.ops)

        # Python2 parses negative ints as an ast.Num with a negative value.
        # Make sure the Num get the precedence of the USub operator in this case.
        if sys.version_info < (3, 0) and isinstance(node, ast.Num):
            if str(node.n)[0] == '-':
                return self.precedences['USub']

        return self.precedences.get(node.__class__.__name__, 0)

    def visit(self, node):
        """
        Visit a node

        Call the correct visit_ method based on the node type.
        Prefer to call the correct method directly if you already know
        the node type.

        :param node: The node to visit
        :type node: ast.Node

        """

        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.visit_Unknown)
        return visitor(node)

    def visit_Unknown(self, node):
        raise RuntimeError('Unknown node %r' % node)

    # region Literals

    def visit_Constant(self, node):
        if node.value in [None, True, False]:
            return self.visit_NameConstant(node)
        elif isinstance(node.value, (int, float, complex)):
            return self.visit_Num(node)
        elif isinstance(node.value, str):
            return self.visit_Str(node)
        elif isinstance(node.value, bytes):
            return self.visit_Bytes(node)
        elif node.value == Ellipsis:
            return self.visit_Ellipsis(node)

        raise RuntimeError('Unknown Constant value %r' % type(node.value))

    def visit_Num(self, node):
        self.token_break()

        v = repr(node.n)

        if v == 'inf':
            self.code += '1e999'
        elif v == '-inf':
            self.code += '-1e999'
        elif v in ['infj', 'inf*j']:
            self.code += '1e999j'
        elif v in ['-infj', '-inf*j']:
            self.code += '-1e999j'

        else:
            if isinstance(node.n, int):
                # Due to the 0x notation, it's unlikely a base-16 literal will be more compact than base-10
                # But for those rare cases....
                h = hex(node.n)
                if len(h) < len(v):
                    v = h

            self.code += v

    def visit_Str(self, node):

        s = repr(node.s)

        if sys.version_info < (3, 0) and self.unicode_literals:
            if s[0] == 'u':
                s = s[1:]
            else:
                s = 'b' + s

        if len(s) > 0 and s[0].isalpha():
            self.token_break()

        self.code += s

    def visit_Bytes(self, node):

        s = repr(node.s)

        if len(s) > 0 and s[0].isalpha():
            self.token_break()

        self.code += s

    def visit_List(self, node):
        self.code += '['
        self._exprlist(node.elts)
        self.code += ']'

    def visit_Tuple(self, node):

        if len(node.elts) == 0:
            self.code += '()'
            return

        self._exprlist(node.elts)

        if len(node.elts) == 1:
            self.code += ','

    def visit_Set(self, node):
        self.code += '{'
        self._exprlist(node.elts)
        self.code += '}'

    def visit_Dict(self, node):
        self.code += '{'

        first = True
        for k, v in zip(node.keys, node.values):
            if not first:
                self.code += ','
            else:
                first = False

            if k is None:
                self.code += '**'
            else:
                self._expression(k)
                self.code += ':'

            self._expression(v)

        self.code += '}'

    def visit_Ellipsis(self, node):
        self.code += '...'

    def visit_NameConstant(self, node):
        self.token_break()
        self.code += repr(node.value)

    # endregion

    # region Variables

    def visit_Name(self, node):
        self.token_break()
        self.code += node.id

    def visit_Starred(self, node):
        self.code += '*'
        self._expression(node.value)

    # endregion

    # region Expressions

    def visit_UnaryOp(self, node):
        self.visit(node.op)

        if sys.version_info < (3, 0) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Num):
            # For: -(1), which is parsed as a UnaryOp(USub, Num(1)).
            # Without this special case it would be printed as -1
            # This is fine, but python 2 will then parse it at Num(-1) so the AST wouldn't round-trip.

            self.code += '('
            self.visit_Num(node.operand)
            self.code += ')'
            return

        self._rhs(node.operand, node)

    def visit_UAdd(self, node):
        self.code += '+'

    def visit_USub(self, node):
        self.code += '-'

    def visit_Not(self, node):
        self.token_break()
        self.code += 'not'

    def visit_Invert(self, node):
        self.code += '~'

    def visit_BinOp(self, node):
        self._lhs(node.left, node.op)
        self.visit(node.op)
        self._rhs(node.right, node.op)

    def visit_Add(self, node):
        self.code += '+'

    def visit_Sub(self, node):
        self.code += '-'

    def visit_Mult(self, node):
        self.code += '*'

    def visit_Div(self, node):
        self.code += '/'

    def visit_FloorDiv(self, node):
        self.code += '//'

    def visit_Mod(self, node):
        self.code += '%'

    def visit_Pow(self, node):
        self.code += '**'

    def visit_LShift(self, node):
        self.code += '<<'

    def visit_RShift(self, node):
        self.code += '>>'

    def visit_BitOr(self, node):
        self.code += '|'

    def visit_BitXor(self, node):
        self.code += '^'

    def visit_BitAnd(self, node):
        self.code += '&'

    def visit_MatMult(self, node):
        self.code += '@'

    def visit_BoolOp(self, node):
        first = True

        op_precedence = self.precedence(node.op)

        for v in node.values:
            if first:
                first = False
            else:
                self._expression(node.op)

            value_precedence = self.precedence(v)

            if value_precedence != 0 and (
                (op_precedence > value_precedence)
                or op_precedence == value_precedence
                and self._is_left_associative(node.op)
            ):
                self.code += '('
                self._expression(v)
                self.code += ')'
            else:
                self._expression(v)

    def visit_And(self, node):
        self.token_break()
        self.code += 'and'

    def visit_Or(self, node):
        self.token_break()
        self.code += 'or'

    def visit_Compare(self, node):

        left_precedence = self.precedence(node.left)
        op_precedence = self.precedence(node.ops[0])

        if left_precedence != 0 and ((op_precedence > left_precedence) or (op_precedence == left_precedence)):
            self.code += '('
            self._expression(node.left)
            self.code += ')'
        else:
            self._expression(node.left)

        for op, comparator in zip(node.ops, node.comparators):
            self._expression(op)
            self._rhs(comparator, op)

    def visit_Eq(self, node):
        self.code += '=='

    def visit_NotEq(self, node):
        self.code += '!='

    def visit_Lt(self, node):
        self.code += '<'

    def visit_LtE(self, node):
        self.code += '<='

    def visit_Gt(self, node):
        self.code += '>'

    def visit_GtE(self, node):
        self.code += '>='

    def visit_Is(self, node):
        self.token_break()
        self.code += 'is'

    def visit_IsNot(self, node):
        self.token_break()
        self.code += 'is not'

    def visit_In(self, node):
        self.token_break()
        self.code += 'in'

    def visit_NotIn(self, node):
        self.token_break()
        self.code += 'not in'

    def visit_Call(self, node):

        self._lhs(node.func, node)

        self.code += '('

        first = True
        for arg in node.args:
            if first:
                first = False
            else:
                self.code += ','

            self._expression(arg)

        if node.keywords:
            for kwarg in node.keywords:
                if first:
                    first = False
                else:
                    self.code += ','

                assert isinstance(kwarg, ast.keyword)
                self.visit_keyword(kwarg)

        if hasattr(node, 'starargs') and node.starargs is not None:
            if first:
                first = False
            else:
                self.code += ','

            self.code += '*'
            self._expression(node.starargs)

        if hasattr(node, 'kwargs') and node.kwargs is not None:
            if not first:
                self.code += ','

            self.code += '**'
            self.visit(node.kwargs)

        self.code += ')'

    def visit_keyword(self, node):
        if node.arg is None:
            self.code += '**'
            self._expression(node.value)
        else:
            self.code += node.arg + '='
            self._expression(node.value)

    def visit_IfExp(self, node):

        self._rhs(node.body, node)

        self.token_break()
        self.code += 'if'

        self._rhs(node.test, node)

        self.token_break()
        self.code += 'else'

        self._expression(node.orelse)

    def visit_Attribute(self, node):
        self.token_break()

        value_precedence = self.precedence(node.value)
        attr_precedence = self.precedence(node)

        if (value_precedence != 0 and (attr_precedence > value_precedence)) or isinstance(node.value, ast.Num):
            self.code += '('
            self._expression(node.value)
            self.code += ')'
        else:
            self._expression(node.value)

        self.code += '.' + node.attr

    # endregion

    # region Subscripting

    def visit_Subscript(self, node):

        value_precedence = self.precedence(node.value)
        slice_precedence = 17  # self.precedence(node)

        if value_precedence != 0 and (slice_precedence > value_precedence):
            self.code += '('
            self._expression(node.value)
            self.code += ')'
        else:
            self._expression(node.value)

        self.code += '['

        if isinstance(node.slice, ast.Index):
            self.visit_Index(node.slice)
        elif isinstance(node.slice, ast.Slice):
            self.visit_Slice(node.slice)
        elif isinstance(node.slice, ast.ExtSlice):
            self.visit_ExtSlice(node.slice)
        elif isinstance(node.slice, ast.Ellipsis):
            self.visit_Ellipsis(node)
        else:
            raise AssertionError('Unknown slice type %r' % node.slice)

        self.code += ']'

    def visit_Index(self, node):
        self._expression(node.value)

    def visit_Slice(self, node):
        if node.lower:
            self._expression(node.lower)
        self.code += ':'
        if node.upper:
            self._expression(node.upper)
        if node.step:
            self.code += ':'
            self._expression(node.step)

    def visit_ExtSlice(self, node):
        first = True

        for s in node.dims:
            if not first:
                self.code += ','
            else:
                first = False

            self._expression(s)

        if len(node.dims) == 1:
            self.code += ','

    # endregion

    # region Comprehensions

    def visit_ListComp(self, node):
        self.code += '['
        self._expression(node.elt)
        [self.visit_comprehension(x) for x in node.generators]
        self.code += ']'

    def visit_SetComp(self, node):
        self.code += '{'
        self._expression(node.elt)
        [self.visit_comprehension(x) for x in node.generators]
        self.code += '}'

    def visit_GeneratorExp(self, node):
        self.code += '('
        self._expression(node.elt)
        [self.visit_comprehension(x) for x in node.generators]
        self.code += ')'

    def visit_DictComp(self, node):
        self.code += '{'
        self._expression(node.key)
        self.code += ':'
        self._expression(node.value)
        [self.visit_comprehension(x) for x in node.generators]
        self.code += '}'

    def visit_comprehension(self, node):
        assert isinstance(node, ast.comprehension)

        self.token_break()

        if hasattr(node, 'is_async') and node.is_async:
            self.code += 'async '

        self.code += 'for'
        self._exprlist([node.target])
        self.token_break()
        self.code += 'in'

        self._rhs(node.iter, node)

        if node.ifs:
            for i in node.ifs:
                self.token_break()
                self.code += 'if'
                self._rhs(i, node)

    # endregion

    # region Function and Class definitions

    def visit_Lambda(self, node):

        self.token_break()
        self.code += 'lambda'

        self.visit_arguments(node.args)

        self.code += ':'

        self._expression(node.body)

    def visit_arguments(self, node):
        first = True

        args = getattr(node, 'posonlyargs', []) + node.args

        count_no_defaults = len(args) - len(node.defaults)
        for i, arg in enumerate(args):
            if not first:
                self.code += ','
            else:
                self.token_break()
                first = False

            self._expression(arg)

            if i >= count_no_defaults:
                self.code += '='
                self._expression(node.defaults[i - count_no_defaults])

            if hasattr(node, 'posonlyargs') and node.posonlyargs and i + 1 == len(node.posonlyargs):
                self.code += ',/'

        if node.vararg:
            if not first:
                self.code += ','
            else:
                self.token_break()
                first = False

            self.code += '*'

            if hasattr(node, 'varargannotation'):
                self.code += node.vararg
                if node.varargannotation is not None:
                    self.code += ':'
                    self._expression(node.varargannotation)
            elif isinstance(node.vararg, str):
                self.code += node.vararg
            else:
                self.visit(node.vararg)

        if hasattr(node, 'kwonlyargs') and node.kwonlyargs:

            if not node.vararg:
                if not first:
                    self.code += ','
                else:
                    self.token_break()
                    first = False

                self.code += '*'

            for i, arg in enumerate(node.kwonlyargs):
                self.code += ','
                self.visit_arg(arg)

                if node.kw_defaults[i] is not None:
                    self.code += '='
                    self._expression(node.kw_defaults[i])

        if node.kwarg:
            if not first:
                self.code += ','
            else:
                self.token_break()
                first = False

            self.code += '**'

            if hasattr(node, 'kwargannotation'):
                self.code += node.kwarg
                if node.kwargannotation is not None:
                    self.code += ':'
                    self._expression(node.kwargannotation)
            elif isinstance(node.kwarg, str):
                self.code += node.kwarg
            else:
                self.visit(node.kwarg)

    def visit_arg(self, node):
        if isinstance(node, ast.Name):
            # Python 2 uses Name nodes
            return self.visit_Name(node)

        self.code += node.arg

        if node.annotation:
            self.code += ':'
            self._expression(node.annotation)

    def visit_Repr(self, node):
        self.code += '`'
        self._expression(node.value)
        self.code += '`'

    # endregion

    def visit_Expression(self, node):
        self._expression(node.body)

    def _expression(self, expression):
        if isinstance(expression, ast.Yield) or (hasattr(ast, 'YieldFrom') and isinstance(expression, ast.YieldFrom)):
            self.code += '('
            self._yield_expr(expression)
            self.code += ')'
        elif isinstance(expression, ast.Tuple) and len(expression.elts) > 0:
            self.code += '('
            self.visit_Tuple(expression)
            self.code += ')'
        elif hasattr(ast, 'NamedExpr') and isinstance(expression, ast.NamedExpr):
            self.code += '('
            self.visit_NamedExpr(expression)
            self.code += ')'
        else:
            self.visit(expression)

    def _testlist(self, test):
        if isinstance(test, ast.Yield) or (hasattr(ast, 'YieldFrom') and isinstance(test, ast.YieldFrom)):
            self.code += '('
            self._yield_expr(test)
            self.code += ')'
        elif hasattr(ast, 'NamedExpr') and isinstance(test, ast.NamedExpr):
            self.code += '('
            self.visit_NamedExpr(test)
            self.code += ')'
        else:
            self.visit(test)

    def _exprlist(self, exprlist):
        first = True

        for expr in exprlist:
            if first:
                first = False
            else:
                self.code += ','
            self._expression(expr)

    def _yield_expr(self, yield_node):
        self.token_break()

        if isinstance(yield_node, ast.Yield):
            self.code += 'yield'
        elif isinstance(yield_node, ast.YieldFrom):
            self.code += 'yield from'

        if yield_node.value is not None:
            self._expression(yield_node.value)

    @staticmethod
    def _is_right_associative(operator):
        return isinstance(operator, ast.Pow)

    @staticmethod
    def _is_left_associative(operator):
        return not isinstance(operator, ast.Pow)

    def _lhs(self, left_node, op_node):
        left_precedence = self.precedence(left_node)
        op_precedence = self.precedence(op_node)

        if left_precedence != 0 and (
            (op_precedence > left_precedence)
            or (op_precedence == left_precedence and self._is_right_associative(op_node))
        ):
            self.code += '('
            self._expression(left_node)
            self.code += ')'
        else:
            self._expression(left_node)

    def _rhs(self, right_node, op_node):
        right_precedence = self.precedence(right_node)
        op_precedence = self.precedence(op_node)

        if right_precedence != 0 and (
            (op_precedence > right_precedence)
            or (op_precedence == right_precedence and self._is_left_associative(op_node))
        ):
            self.code += '('
            self._expression(right_node)
            self.code += ')'
        else:
            self._expression(right_node)

    def token_break(self):
        if len(self.code) == 0:
            return

        if self.code[-1] not in '[]{}() :"\'=\n\t<>|^&+-*@/%;,':
            self.code += ' '

    def visit_JoinedStr(self, node):
        assert isinstance(node, ast.JoinedStr)

        import python_minifier.f_string

        self.token_break()
        self.code += str(python_minifier.f_string.OuterFString(node))

    def visit_NamedExpr(self, node):
        self._expression(node.target)
        self.code += ':='
        self._expression(node.value)

    def visit_Await(self, node):
        assert isinstance(node, ast.Await)
        self.token_break()
        self.code += 'await'
        self._rhs(node.value, node)