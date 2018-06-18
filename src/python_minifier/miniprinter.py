import ast
import sys

class MiniPrinter(object):
    """
    Builds the smallest possible exact representation of an ast
    """

    def __init__(self, indent_char='\t'):

        self.code = ''
        self.indent = 0
        self.indent_char = indent_char

        self.unicode_literals = False

        self.precedences = {
            'Lambda': 2,
            'IfExp': 3,
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
            'comprehension': 18
        }

    def __call__(self, module):
        """
        Generate the source code for an AST

        :param module: The Module to generate code for
        :type module: ast.Module
        :rtype: str

        """

        self.visit_Module(module)
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

        if isinstance(node, ast.BinOp):
            return self.precedences[node.op.__class__.__name__]
        elif isinstance(node, ast.UnaryOp):
            return self.precedences[node.op.__class__.__name__]
        elif isinstance(node, ast.BoolOp):
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

    def newline(self):
        """
        Ensure there is a newline at the end of the output
        """

        self.code = self.code.rstrip('\n' + self.indent_char + ';')
        self.code += '\n'
        self.code += self.indent_char * self.indent

    def visit_Unknown(self, node):
        raise RuntimeError('Unknown node %r' % node)

    # region Simple Statements

    def visit_Exec(self, node):
        assert isinstance(node, ast.Exec)

        self.token_break()

        self.code += 'exec'
        self._expression(node.body)

        if node.globals:
            self.token_break()
            self.code += 'in'
            self._expression(node.globals)

        if node.locals:
            self.code += ','
            self._expression(node.locals)

        self.end_statement()

    def visit_Expr(self, node):
        assert isinstance(node, ast.Expr)

        self._testlist(node.value)
        self.end_statement()

    def visit_Assert(self, node):
        assert isinstance(node, ast.Assert)

        self.token_break()

        self.code += 'assert'
        self._expression(node.test)

        if node.msg:
            self.code += ','
            self._expression(node.msg)

        self.end_statement()

    def visit_Assign(self, node):
        assert isinstance(node, ast.Assign)

        for target_node in node.targets:
            self._testlist(target_node)
            self.code += '='

        # Yield nodes that are the sole node on the right hand side of an assignment do not need parens
        if isinstance(node.value, ast.Expr) and isinstance(node.value.value, ast.Yield):
            self._yield_expr(node.value)
        elif isinstance(node.value, ast.Expr) and isinstance(node.value.value, ast.YieldFrom):
            self._yield_expr(node.value)
        else:
            self._testlist(node.value)

        self.end_statement()

    def visit_AugAssign(self, node):
        assert isinstance(node, ast.AugAssign)

        self._testlist(node.target)
        self.visit(node.op)
        self.code += '='

        # Yield nodes that are the sole node on the right hand side of an assignment do not need parens
        if isinstance(node.value, ast.Expr) and isinstance(node.value.value, ast.Yield):
            self._yield_expr(node.value)
        elif isinstance(node.value, ast.Expr) and isinstance(node.value.value, ast.YieldFrom):
            self._yield_expr(node.value)
        else:
            self._testlist(node.value)

        self.end_statement()

    def visit_AnnAssign(self, node):
        assert isinstance(node, ast.AnnAssign)

        if node.simple:
            self.visit(node.target)
        else:
            self.code += '('
            self._expression(node.target)
            self.code += ')'

        if node.annotation:
            self.code += ':'
            self._expression(node.annotation)

        if node.value:
            self.code += '='

            # Yield nodes that are the sole node on the right hand side of an assignment do not need parens
            if isinstance(node.value, ast.Expr) and isinstance(node.value.value, ast.Yield):
                self._yield_expr(node.value)
            elif isinstance(node.value, ast.Expr) and isinstance(node.value.value, ast.YieldFrom):
                self._yield_expr(node.value)
            else:
                self._expression(node.value)

        self.end_statement()

    def visit_Pass(self, node):
        assert isinstance(node, ast.Pass)

        self.token_break()
        self.code += 'pass'
        self.end_statement()

    def visit_Delete(self, node):
        assert isinstance(node, ast.Delete)

        self.code += 'del'
        self._exprlist(node.targets)
        self.end_statement()

    def visit_Return(self, node):
        assert isinstance(node, ast.Return)

        self.token_break()
        self.code += 'return'
        if node.value is not None:
            self._expression(node.value)
        self.end_statement()

    def visit_Print(self, node):
        assert isinstance(node, ast.Print)

        self.code += 'print'

        first = True

        if node.dest:
            self.code += '>>'
            self._expression(node.dest)
            first = False

        for v in node.values:
            if first:
                first = False
            else:
                self.code += ','

            self._expression(v)

        if not node.nl:
            self.code += ','

        self.end_statement()

    def visit_Yield(self, node):
        assert isinstance(node, ast.Yield)

        self._yield_expr(node)
        self.end_statement()

    def visit_YieldFrom(self, node):
        assert isinstance(node, ast.YieldFrom)

        self._yield_expr(node)
        self.end_statement()

    def visit_Raise(self, node):
        assert isinstance(node, ast.Raise)

        self.code += 'raise'

        if hasattr(node, 'type'):
            # Python2 raise node

            if node.type:
                self.code += ' '
                self._expression(node.type)
            if node.inst:
                self.code += ','
                self._expression(node.inst)
            if node.tback:
                self.code += ','
                self._expression(node.tback)

        else:
            # Python3

            if node.exc:
                self.code += ' '
                self._expression(node.exc)

            if node.cause:
                self.code += ' from '
                self._expression(node.cause)

        self.end_statement()

    def visit_Break(self, node):
        assert isinstance(node, ast.Break)

        self.token_break()
        self.code += 'break'
        self.end_statement()

    def visit_Continue(self, node):
        assert isinstance(node, ast.Continue)

        self.token_break()
        self.code += 'continue'
        self.end_statement()

    def visit_Import(self, node):
        assert isinstance(node, ast.Import)

        self.code += 'import '

        first = True
        for n in node.names:
            if first:
                first = False
            else:
                self.code += ','

            self.visit_alias(n)

        self.end_statement()

    def visit_ImportFrom(self, node):
        assert isinstance(node, ast.ImportFrom)

        if node.module is None:
            self.code += 'from ' + ('.' * node.level) + ' '
        else:
            self.code += 'from ' + ('.' * node.level)
            self.code += node.module

        self.code += ' import '
        first = True
        for n in node.names:
            if first:
                first = False
            else:
                self.code += ','

            if node.module == '__future__' and n.name == 'unicode_literals':
                self.unicode_literals = True

            self.visit_alias(n)

        self.end_statement()

    def visit_alias(self, node):
        assert isinstance(node, ast.alias)

        self.code += node.name

        if node.asname:
            self.code += ' as ' + node.asname

    def visit_Global(self, node):
        assert isinstance(node, ast.Global)

        self.code += 'global ' + ','.join(node.names)
        self.end_statement()

    def visit_Nonlocal(self, node):
        assert isinstance(node, ast.Nonlocal)

        self.code += 'nonlocal ' + ','.join(node.names)
        self.end_statement()

    # endregion

    # region Compound Statements

    def visit_If(self, node, el=False):
        assert isinstance(node, ast.If)

        self.newline()

        if el:
            self.code += 'el'
        self.code += 'if'
        self._expression(node.test)
        self.code += ':'

        self._suite(node.body)

        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                # elif
                self.visit_If(node.orelse[0], el=True)
                self.newline()
            else:
                # an else block
                self.code += 'else:'
                self._suite(node.orelse)

    def visit_For(self, node, is_async=False):
        assert isinstance(node, ast.For) or (hasattr(ast, 'AsyncFor') and isinstance(node, ast.AsyncFor))

        self.newline()

        if is_async:
            self.code += 'async '

        self.code += 'for '
        self._exprlist([node.target])
        self.code += ' in '
        self._expression(node.iter)
        self.code += ':'

        self._suite(node.body)

        if node.orelse:
            self.newline()
            self.code += 'else:'
            self._suite(node.orelse)

    def visit_While(self, node):
        assert isinstance(node, ast.While)

        self.newline()
        self.code += 'while '
        self._expression(node.test)
        self.code += ':'
        self._suite(node.body)

        if node.orelse:
            self.code += 'else:'
            self._suite(node.orelse)

    def visit_Try(self, node):
        assert isinstance(node, ast.Try)

        self.newline()
        self.code += 'try:'
        self._suite(node.body)

        [self.visit_ExceptHandler(n) for n in node.handlers]

        if node.orelse:
            self.code += 'else:'
            self._suite(node.orelse)

        if node.finalbody:
            self.code += 'finally:'
            self._suite(node.finalbody)

    def visit_TryFinally(self, node):
        assert isinstance(node, ast.TryFinally)

        if len(node.body) == 1 and isinstance(node.body[0], ast.TryExcept):
            self.visit_TryExcept(node.body[0])
        else:
            self.newline()
            self.code += 'try:'
            self._suite(node.body)

        if node.finalbody:
            self.code += 'finally:'
            self._suite(node.finalbody)

    def visit_TryExcept(self, node):
        assert isinstance(node, ast.TryExcept)

        self.newline()
        self.code += 'try:'
        self._suite(node.body)

        [self.visit_ExceptHandler(n) for n in node.handlers]

        if node.orelse:
            self.code += 'else:'
            self._suite(node.orelse)

    def visit_ExceptHandler(self, node):
        assert isinstance(node, ast.ExceptHandler)

        self.code += 'except'
        if node.type is not None:
            self.code += ' '
            self._expression(node.type)

        if node.name is not None:
            self.token_break()
            self.code += 'as'

            if isinstance(node.name, str):
                self.code += ' ' + node.name
            else:
                self._expression(node.name)

        self.code += ':'

        self._suite(node.body)

    def visit_With(self, node, is_async=False):
        assert isinstance(node, ast.With) or (hasattr(ast, 'AsyncWith') and isinstance(node, ast.AsyncWith))

        self.newline()

        if is_async:
            self.code += 'async '

        self.code += 'with'

        first = True
        if hasattr(node, 'items'):

            for item in node.items:
                if first:
                    first = False
                else:
                    self.code += ','

                if self.precedence(item.context_expr) != 0 and self.precedence(item.context_expr) <= self.precedence(
                        node
                ):
                    self.code += '('
                    self.visit_withitem(item)
                    self.code += ')'
                else:
                    self.visit_withitem(item)
        else:
            self.visit_withitem(node)

        self.code += ':'
        self._suite(node.body)

    def visit_withitem(self, node):
        assert (hasattr(ast, 'withitem') and isinstance(node, ast.withitem)) or isinstance(node, ast.With)

        self._expression(node.context_expr)

        if node.optional_vars is not None:
            self.token_break()
            self.code += 'as'
            self._expression(node.optional_vars)

    def visit_FunctionDef(self, node, is_async=False):
        assert isinstance(node, ast.FunctionDef) or (
                hasattr(ast, 'AsyncFunctionDef') and isinstance(node, ast.AsyncFunctionDef)
        )

        self.newline()

        for d in node.decorator_list:
            self.code += '@'
            self.visit(d)
            self.newline()

        if is_async:
            self.code += 'async '

        self.code += 'def ' + node.name + '('
        self.visit_arguments(node.args)
        self.code += ')'

        if hasattr(node, 'returns') and node.returns:
            self.code += '->'
            self._expression(node.returns)
            self.code += ':'
        else:
            self.code += ':'

        if hasattr(node, 'docstring') and node.docstring is not None:
            self._suite([ast.Expr(value=ast.Str(s=node.docstring))] + node.body)
        else:
            self._suite(node.body)

    def visit_ClassDef(self, node):
        assert isinstance(node, ast.ClassDef)

        self.newline()

        for d in node.decorator_list:
            self.code += '@'
            self.visit(d)
            self.newline()

        first = True
        self.code += 'class ' + node.name

        for b in node.bases:
            if first:
                self.code += '('
                first = False
            else:
                self.code += ','
            self._expression(b)

        if hasattr(node, 'starargs') and node.starargs is not None:
            if first:
                self.code += '('
                first = False
            else:
                self.code += ','

            self.code += '*'
            self._expression(node.starargs)

        if hasattr(node, 'keywords'):
            for kw in node.keywords:
                if first:
                    self.code += '('
                    first = False
                else:
                    self.code += ','
                self.visit_keyword(kw)

        if hasattr(node, 'kwargs') and node.kwargs is not None:
            if first:
                self.code += '('
                first = False
            else:
                self.code += ','

            self.code += '**'
            self.visit(node.kwargs)

        if not first:
            self.code += ')'

        self.code += ':'

        if hasattr(node, 'docstring') and node.docstring is not None:
            self._suite([ast.Expr(value=ast.Str(s=node.docstring))] + node.body)
        else:
            self._suite(node.body)

    # endregion

    # region async and await

    def visit_AsyncFunctionDef(self, node):
        assert isinstance(node, ast.AsyncFunctionDef)
        self.visit_FunctionDef(node, is_async=True)

    def visit_Await(self, node):
        assert isinstance(node, ast.Await)
        self.token_break()
        self.code += 'await'
        self._rhs(node.value, node)

    def visit_AsyncFor(self, node):
        assert isinstance(node, ast.AsyncFor)
        self.visit_For(node, is_async=True)

    def visit_AsyncWith(self, node):
        assert isinstance(node, ast.AsyncWith)
        self.visit_With(node, is_async=True)

    # endregion

    # region Literals

    def visit_Num(self, node):
        self.token_break()

        v = repr(node.n)

        if v == 'inf':
            self.code += '1e999'
        elif v == '-inf':
            self.code += '-1e999'
        elif v == 'infj':
            self.code += '1e999j'
        elif v == '-infj':
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

            value_precendence = self.precedence(v)

            if value_precendence != 0 and (
                    (op_precedence > value_precendence)
                    or op_precedence == value_precendence
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

        if node.args:
            self.token_break()
            self.visit_arguments(node.args)

        self.code += ':'

        self._expression(node.body)

    def visit_arguments(self, node):
        first = True

        count_no_defaults = len(node.args) - len(node.defaults)
        for i, arg in enumerate(node.args):
            if not first:
                self.code += ','
            else:
                first = False

            self._expression(arg)

            if i >= count_no_defaults:
                self.code += '='
                self._expression(node.defaults[i - count_no_defaults])

        if node.vararg:
            if not first:
                self.code += ','
            else:
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

    def visit_Module(self, node):
        if hasattr(node, 'docstring') and node.docstring is not None:
            # Python 3.6 added a docstring field! Really useful for every use case except this one...
            # Put the docstring back into the body
            self._suite_body([ast.Expr(value=ast.Str(s=node.docstring))] + node.body)
        else:
            self._suite_body(node.body)

    def _expression(self, expression):
        if isinstance(expression, ast.Yield) or (hasattr(ast, 'YieldFrom') and isinstance(expression, ast.YieldFrom)):
            self.code += '('
            self._yield_expr(expression)
            self.code += ')'
        elif isinstance(expression, ast.Tuple) and len(expression.elts) > 0:
            self.code += '('
            self.visit_Tuple(expression)
            self.code += ')'
        else:
            self.visit(expression)

    def _testlist(self, test):
        if isinstance(test, ast.Yield) or (hasattr(ast, 'YieldFrom') and isinstance(test, ast.YieldFrom)):
            self.code += '('
            self._yield_expr(test)
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

    def _suite(self, node_list):

        compound_statements = [
            'For',
            'While',
            'Try',
            'If',
            'With',
            'ClassDef',
            'TryFinally',
            'TryExcept',
            'FunctionDef',
            'AsyncFunctionDef',
            'AsyncFor',
            'AsyncWith',
        ]

        if len(node_list) == 1 and node_list[0].__class__.__name__ not in compound_statements:
            self._suite_body(node_list)
            self.newline()
        else:
            self.enter_block()
            self._suite_body(node_list)
            self.leave_block()

    def _suite_body(self, node_list):

        statements = {
            'Assign': self.visit_Assign,
            'AnnAssign': self.visit_AnnAssign,
            'AugAssign': self.visit_AugAssign,
            'Expr': self.visit_Expr,
            'Delete': self.visit_Delete,
            'Pass': self.visit_Pass,
            'Import': self.visit_Import,
            'ImportFrom': self.visit_ImportFrom,
            'Global': self.visit_Global,
            'Nonlocal': self.visit_Nonlocal,
            'Assert': self.visit_Assert,
            'Break': self.visit_Break,
            'Continue': self.visit_Continue,
            'Return': self.visit_Return,
            'Raise': self.visit_Raise,
            'Yield': self.visit_Yield,
            'YieldFrom': self.visit_YieldFrom,
            'For': self.visit_For,
            'While': self.visit_While,
            'Try': self.visit_Try,
            'If': self.visit_If,
            'With': self.visit_With,
            'ClassDef': self.visit_ClassDef,
            'FunctionDef': self.visit_FunctionDef,
            'AsyncFunctionDef': self.visit_AsyncFunctionDef,
            'AsyncFor': self.visit_AsyncFor,
            'AsyncWith': self.visit_AsyncWith,
            'TryFinally': self.visit_TryFinally,
            'TryExcept': self.visit_TryExcept,
            'Print': self.visit_Print,
            'Exec': self.visit_Exec,
        }

        for node in node_list:
            statements[node.__class__.__name__](node)

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

        if right_precedence != 0 and ((op_precedence > right_precedence) or (
                op_precedence == right_precedence and self._is_left_associative(op_node))):
            self.code += '('
            self._expression(right_node)
            self.code += ')'
        else:
            self._expression(right_node)

    def enter_block(self):
        self.indent += 1
        self.newline()

    def leave_block(self):
        self.indent -= 1
        self.newline()

    def token_break(self):
        if len(self.code) == 0:
            return

        if self.code[-1].isalnum() or self.code[-1] == '_':
            self.code += ' '

    def end_statement(self):
        """ End a statement with a newline, or a semi-colon if it saves characters. """

        if self.indent == 0:
            self.newline()
        else:
            if self.code[-1] != ';':
                self.code += ';'
