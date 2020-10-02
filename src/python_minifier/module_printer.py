import ast

from .expression_printer import ExpressionPrinter


class ModulePrinter(ExpressionPrinter):
    """
    Builds the smallest possible exact representation of an ast
    """

    def __init__(self, indent_char='\t'):
        super(ModulePrinter, self).__init__()
        self.indent_char = indent_char

    def __call__(self, module):
        """
        Generate the source code for an AST

        :param module: The Module to generate code for
        :type module: ast.Module
        :rtype: str

        """

        assert isinstance(module, ast.Module)

        self.visit_Module(module)
        self.code = self.code.rstrip('\n' + self.indent_char + ';')
        return self.code

    def newline(self):
        """
        Ensure there is a newline at the end of the output
        """
        if self.code == '':
            return

        self.code = self.code.rstrip('\n' + self.indent_char + ';')
        self.code += '\n'
        self.code += self.indent_char * self.indent

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

        if isinstance(node.value, ast.Yield):
            self._yield_expr(node.value)
        elif hasattr(ast, 'YieldFrom') and isinstance(node.value, ast.YieldFrom):
            self._yield_expr(node.value)
        else:
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
        if isinstance(node.value, ast.Yield):
            self._yield_expr(node.value)
        elif hasattr(ast, 'YieldFrom') and isinstance(node.value, ast.YieldFrom):
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
        if isinstance(node.value, ast.Yield):
            self._yield_expr(node.value)
        elif hasattr(ast, 'YieldFrom') and isinstance(node.value, ast.YieldFrom):
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
            self._testlist(node.value)
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

        if hasattr(node, 'returns') and node.returns is not None:
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

    def visit_AsyncFor(self, node):
        assert isinstance(node, ast.AsyncFor)
        self.visit_For(node, is_async=True)

    def visit_AsyncWith(self, node):
        assert isinstance(node, ast.AsyncWith)
        self.visit_With(node, is_async=True)

    # endregion

    def visit_Module(self, node):
        if hasattr(node, 'docstring') and node.docstring is not None:
            # Python 3.6 added a docstring field! Really useful for every use case except this one...
            # Put the docstring back into the body
            self._suite_body([ast.Expr(value=ast.Str(s=node.docstring))] + node.body)
        else:
            self._suite_body(node.body)

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

        if [node for node in node_list if node.__class__.__name__ in compound_statements]:
            self.enter_block()
            self._suite_body(node_list)
            self.leave_block()
        else:
            self.indent += 1
            self._suite_body(node_list)
            self.indent -= 1
            self.newline()

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

    def enter_block(self):
        self.indent += 1
        self.newline()

    def leave_block(self):
        self.indent -= 1
        self.newline()

    def end_statement(self):
        """ End a statement with a newline, or a semi-colon if it saves characters. """

        if self.indent == 0:
            self.newline()
        else:
            if self.code[-1] != ';':
                self.code += ';'
