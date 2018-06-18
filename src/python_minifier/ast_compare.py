class CompareError(RuntimeError):
    """
    Raised when an AST compares unequal.
    """

    def __init__(self, namespace, lnode, rnode, msg=None):
        self.namespace = namespace
        self.lnode = lnode
        self.rnode = rnode
        self.msg = msg

    def __repr__(self):
        return 'NodeError(%r, %r)' % (self.lnode, self.rnode)

    def __str__(self):
        error = ''

        if self.msg:
            error += self.msg

        if self.namespace:
            error += ' in namespace ' + '.'.join(self.namespace) + ' '

        if self.lnode and hasattr(self.lnode, 'lineno'):
            error += ' at source %i:%i:' % (self.lnode.lineno, self.lnode.col_offset)

        return error


class AstComparer:
    """
    Compare Python Abstract Syntax Trees

    >>> comparer = AstComparer()
    >>> comparer(l_ast, r_ast)

    After instantiating, call with two ASTs.
    If they are not identical, an exception will be raised.

    """

    def __init__(self):
        self.namespaces = []

    def __call__(self, l_ast, r_ast):
        return self.compare(l_ast, r_ast)

    def compare(self, lnode, rnode):
        if type(lnode) != type(rnode):
            raise CompareError(
                self.namespaces, lnode, rnode, msg='Nodes do not match! rnode=%r, lnode=%r' % (lnode, rnode)
            )

        if lnode is None:
            return

        method = 'compare_' + lnode.__class__.__name__
        v = getattr(self, method)

        v(lnode, rnode)

    def compare_list(self, llist, rlist):

        if len(llist) != len(rlist):
            raise CompareError(
                self.namespaces,
                llist[0] if len(llist) else None,
                rlist[0] if len(rlist) else None,
                'Node list does not have the same number of elements',
            )

        for l, r in zip(llist, rlist):
            self.compare(l, r)

    def compare_Exec(self, lnode, rnode):
        self.compare(lnode.body, rnode.body)
        self.compare(lnode.locals, rnode.locals)
        self.compare(lnode.globals, rnode.globals)

    # region Literals

    def compare_Num(self, lnode, rnode):
        if lnode.n != rnode.n:
            raise CompareError(self.namespaces, lnode, rnode, 'Num values do not match')

    def compare_Str(self, lnode, rnode):
        if lnode.s != rnode.s:
            raise CompareError(self.namespaces, lnode, rnode, 'String values do not match')

    def compare_FormattedValue(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)
        if lnode.conversion != rnode.conversion:
            raise CompareError(self.namespaces, lnode, rnode, 'FormattedValue conversions do not match')
        self.compare(lnode.format_spec, rnode.format_spec)

    def compare_JoinedStr(self, lnode, rnode):
        self.compare_list(lnode.values, rnode.values)

    def compare_Bytes(self, lnode, rnode):
        if lnode.s != rnode.s:
            raise CompareError(self.namespaces, lnode, rnode, 'Bytes values do not match')

    def compare_List(self, lnode, rnode):
        self.compare_list(lnode.elts, rnode.elts)

    def compare_Tuple(self, lnode, rnode):
        self.compare_list(lnode.elts, rnode.elts)

    def compare_Set(self, lnode, rnode):
        self.compare_list(lnode.elts, rnode.elts)

    def compare_Dict(self, lnode, rnode):
        self.compare_list(lnode.keys, rnode.keys)
        self.compare_list(lnode.values, rnode.values)

    def compare_Ellipsis(self, lnode, rnode):
        pass

    def compare_NameConstant(self, lnode, rnode):
        if lnode.value != rnode.value:
            raise CompareError(self.namespaces, lnode, rnode, 'Constant values do not match')

    # endregion

    # region Variables

    def compare_Name(self, lnode, rnode):
        if lnode.id != rnode.id:
            raise CompareError(self.namespaces, lnode, rnode, 'Name values do not match')

    def compare_Starred(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    # endregion

    # region Expressions

    def compare_Repr(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    def compare_Expr(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    def compare_UnaryOp(self, lnode, rnode):
        self.compare(lnode.op, rnode.op)
        self.compare(lnode.operand, rnode.operand)

    def compare_UAdd(self, lnode, rnode):
        pass

    def compare_USub(self, lnode, rnode):
        pass

    def compare_Not(self, lnode, rnode):
        pass

    def compare_Invert(self, lnode, rnode):
        pass

    def compare_BinOp(self, lnode, rnode):
        self.compare(lnode.left, rnode.left)
        self.compare(lnode.op, rnode.op)
        self.compare(lnode.right, rnode.right)

    def compare_Add(self, lnode, rnode):
        pass

    def compare_Sub(self, lnode, rnode):
        pass

    def compare_Mult(self, lnode, rnode):
        pass

    def compare_Div(self, lnode, rnode):
        pass

    def compare_FloorDiv(self, lnode, rnode):
        pass

    def compare_Mod(self, lnode, rnode):
        pass

    def compare_Pow(self, lnode, rnode):
        pass

    def compare_LShift(self, lnode, rnode):
        pass

    def compare_RShift(self, lnode, rnode):
        pass

    def compare_BitOr(self, lnode, rnode):
        pass

    def compare_BitXor(self, lnode, rnode):
        pass

    def compare_BitAnd(self, lnode, rnode):
        pass

    def compare_MatMult(self, lnode, rnode):
        pass

    def compare_BoolOp(self, lnode, rnode):
        self.compare(lnode.op, rnode.op)
        self.compare_list(lnode.values, rnode.values)

    def compare_And(self, lnode, rnode):
        pass

    def compare_Or(self, lnode, rnode):
        pass

    def compare_Compare(self, lnode, rnode):
        self.compare(lnode.left, rnode.left)
        self.compare_list(lnode.ops, rnode.ops)
        self.compare_list(lnode.comparators, rnode.comparators)

    def compare_Eq(self, lnode, rnode):
        pass

    def compare_NotEq(self, lnode, rnode):
        pass

    def compare_Lt(self, lnode, rnode):
        pass

    def compare_LtE(self, lnode, rnode):
        pass

    def compare_Gt(self, lnode, rnode):
        pass

    def compare_GtE(self, lnode, rnode):
        pass

    def compare_Is(self, lnode, rnode):
        pass

    def compare_IsNot(self, lnode, rnode):
        pass

    def compare_In(self, lnode, rnode):
        pass

    def compare_NotIn(self, lnode, rnode):
        pass

    def compare_Call(self, lnode, rnode):
        self.compare(lnode.func, rnode.func)
        self.compare_list(lnode.args, rnode.args)
        self.compare_list(lnode.keywords, rnode.keywords)

        if hasattr(lnode, 'starargs'):
            self.compare(lnode.starargs, rnode.starargs)
            self.compare(lnode.kwargs, rnode.kwargs)

    def compare_keyword(self, lnode, rnode):
        if lnode.arg != rnode.arg:
            raise CompareError(self.namespaces, lnode, rnode, 'Keyword arg names do not match')
        self.compare(lnode.value, rnode.value)

    def compare_IfExp(self, lnode, rnode):
        self.compare(lnode.test, rnode.test)
        self.compare(lnode.body, rnode.body)
        self.compare(lnode.orelse, rnode.orelse)

    def compare_Attribute(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

        if lnode.attr != rnode.attr:
            raise CompareError(self.namespaces, lnode, rnode, 'Attrs do not match')

    # endregion

    # region Subscripting

    def compare_Subscript(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)
        self.compare(lnode.slice, rnode.slice)

    def compare_Index(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    def compare_Slice(self, lnode, rnode):
        self.compare(lnode.lower, rnode.lower)
        self.compare(lnode.upper, rnode.upper)
        self.compare(lnode.step, rnode.step)

    def compare_ExtSlice(self, lnode, rnode):
        self.compare_list(lnode.dims, rnode.dims)

    # endregion

    # region Comprehensions

    def compare_ListComp(self, lnode, rnode):
        self.compare(lnode.elt, rnode.elt)
        self.compare_list(lnode.generators, rnode.generators)

    def compare_SetComp(self, lnode, rnode):
        self.compare(lnode.elt, rnode.elt)
        self.compare_list(lnode.generators, rnode.generators)

    def compare_GeneratorExp(self, lnode, rnode):
        self.compare(lnode.elt, rnode.elt)
        self.compare_list(lnode.generators, rnode.generators)

    def compare_DictComp(self, lnode, rnode):
        self.compare(lnode.key, rnode.key)
        self.compare(lnode.value, rnode.value)
        self.compare_list(lnode.generators, rnode.generators)

    def compare_comprehension(self, lnode, rnode):
        self.compare(lnode.target, rnode.target)
        self.compare(lnode.iter, rnode.iter)
        self.compare_list(lnode.ifs, rnode.ifs)

        if hasattr(lnode, 'is_async'):
            if lnode.is_async != rnode.is_async:
                raise CompareError(self.namespaces, lnode, rnode, 'Comprehension is_async values do not match')

    # endregion

    # region Statements

    def compare_Assign(self, lnode, rnode):
        self.compare_list(lnode.targets, rnode.targets)
        self.compare(lnode.value, rnode.value)

    def compare_AnnAssign(self, lnode, rnode):
        self.compare(lnode.target, rnode.target)
        self.compare(lnode.annotation, rnode.annotation)
        self.compare(lnode.value, rnode.value)
        if lnode.simple != rnode.simple:
            raise CompareError(self.namespaces, lnode, rnode, 'AnnAssign simple flags do not match')

    def compare_AugAssign(self, lnode, rnode):
        self.compare(lnode.target, rnode.target)
        self.compare(lnode.op, rnode.op)
        self.compare(lnode.value, rnode.value)

    def compare_Print(self, lnode, rnode):
        self.compare(lnode.dest, rnode.dest)
        self.compare_list(lnode.values, rnode.values)

        if lnode.nl != rnode.nl:
            raise CompareError(self.namespaces, lnode, rnode, 'Print nl values do not match')

    def compare_Raise(self, lnode, rnode):

        if hasattr(lnode, 'type'):
            self.compare(lnode.type, rnode.type)
            self.compare(lnode.inst, rnode.inst)
            self.compare(lnode.tback, rnode.tback)
        else:
            self.compare(lnode.exc, rnode.exc)
            self.compare(lnode.cause, rnode.cause)

    def compare_Assert(self, lnode, rnode):
        self.compare(lnode.test, rnode.test)
        self.compare(lnode.msg, rnode.msg)

    def compare_Delete(self, lnode, rnode):
        self.compare_list(lnode.targets, rnode.targets)

    def compare_Pass(self, lnode, rnode):
        pass

    # endregion

    # region Imports

    def compare_Import(self, lnode, rnode):
        self.compare_list(lnode.names, rnode.names)

    def compare_ImportFrom(self, lnode, rnode):
        if lnode.module != rnode.module:
            raise CompareError(self.namespaces, lnode, rnode, 'ImportFrom modules do not match')
        self.compare_list(lnode.names, rnode.names)
        if lnode.level != rnode.level:
            raise CompareError(self.namespaces, lnode, rnode, 'ImportFrom levels do not match')

    def compare_alias(self, lnode, rnode):
        if lnode.name != rnode.name:
            raise CompareError(self.namespaces, lnode, rnode, 'Import alias names do not match')

        if lnode.asname != rnode.asname:
            raise CompareError(self.namespaces, lnode, rnode, 'Import alias asnames do not match')

    # endregion

    # region Control Flow

    def compare_If(self, lnode, rnode):
        self.compare(lnode.test, rnode.test)
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.orelse, rnode.orelse)

    def compare_For(self, lnode, rnode):
        self.compare(lnode.target, rnode.target)
        self.compare(lnode.iter, rnode.iter)
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.orelse, rnode.orelse)

    def compare_While(self, lnode, rnode):
        self.compare(lnode.test, rnode.test)
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.orelse, rnode.orelse)

    def compare_Break(self, lnode, rnode):
        pass

    def compare_Continue(self, lnode, rnode):
        pass

    def compare_Try(self, lnode, rnode):
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.handlers, rnode.handlers)
        self.compare_list(lnode.orelse, rnode.orelse)
        self.compare_list(lnode.finalbody, rnode.finalbody)

    def compare_TryFinally(self, lnode, rnode):
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.finalbody, rnode.finalbody)

    def compare_TryExcept(self, lnode, rnode):
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.handlers, rnode.handlers)
        self.compare_list(lnode.orelse, rnode.orelse)

    def compare_ExceptHandler(self, lnode, rnode):
        self.compare(lnode.type, rnode.type)

        if isinstance(lnode.name, str) and lnode.name != rnode.name:
            raise CompareError(self.namespaces, lnode, rnode, 'ExceptionHander names do not match')
        elif lnode.name == None and lnode.name != rnode.name:
            self.compare(lnode.name, rnode.name)

        self.compare_list(lnode.body, rnode.body)

    def compare_With(self, lnode, rnode):

        if hasattr(lnode, 'items'):
            self.compare_list(lnode.items, rnode.items)
        else:
            self.compare(lnode.context_expr, rnode.context_expr)
            self.compare(lnode.optional_vars, rnode.optional_vars)

    def compare_withitem(self, lnode, rnode):
        self.compare(lnode.context_expr, rnode.context_expr)
        self.compare(lnode.optional_vars, rnode.optional_vars)

    # endregion

    # region Function and Class definitions

    def compare_FunctionDef(self, lnode, rnode):
        if lnode.name != rnode.name:
            raise CompareError(self.namespaces, lnode, rnode, 'FunctionDef names do not match')

        self.namespaces.append(lnode.name)

        self.compare(lnode.args, rnode.args)
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.decorator_list, rnode.decorator_list)

        if hasattr(lnode, 'returns'):
            self.compare(lnode.returns, rnode.returns)

        self.namespaces.pop()

    def compare_Lambda(self, lnode, rnode):
        self.compare(lnode.args, rnode.args)
        self.compare(lnode.body, rnode.body)

    def compare_arguments(self, lnode, rnode):
        self.compare_list(lnode.args, rnode.args)

        if hasattr(lnode, 'kwonlyargs'):
            self.compare_list(lnode.kwonlyargs, rnode.kwonlyargs)

        if isinstance(lnode.vararg, str):
            if lnode.vararg != rnode.vararg:
                raise CompareError(self.namespaces, lnode, rnode, 'varargs do not match')
        else:
            self.compare(lnode.vararg, rnode.vararg)

        if isinstance(lnode.kwarg, str):
            if lnode.kwarg != rnode.kwarg:
                raise CompareError(self.namespaces, lnode, rnode, 'kwargs do not match')
        else:
            self.compare(lnode.kwarg, rnode.kwarg)

        self.compare_list(lnode.defaults, rnode.defaults)

        if hasattr(lnode, 'kw_defaults'):
            self.compare_list(lnode.kw_defaults, rnode.kw_defaults)

        if hasattr(lnode, 'varargannotation'):
            self.compare(lnode.varargannotation, rnode.varargannotation)
            self.compare(lnode.kwargannotation, rnode.kwargannotation)

    def compare_arg(self, lnode, rnode):
        if lnode.arg != rnode.arg:
            raise CompareError(self.namespaces, lnode, rnode, 'arg names do not match')
        self.compare(lnode.annotation, rnode.annotation)

    def compare_Return(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    def compare_Yield(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    def compare_YieldFrom(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    def compare_Global(self, lnode, rnode):
        if lnode.names != rnode.names:
            raise CompareError(self.namespaces, lnode, rnode, 'Global names do not match')

    def compare_Nonlocal(self, lnode, rnode):
        if lnode.names != rnode.names:
            raise CompareError(self.namespaces, lnode, rnode, 'Nonlocal names do not match')

    def compare_ClassDef(self, lnode, rnode):

        if lnode.name != rnode.name:
            raise CompareError(self.namespaces, lnode, rnode, 'Class names do not match')

        self.namespaces.append(lnode.name)

        self.compare_list(lnode.bases, rnode.bases)

        if hasattr(lnode, 'keywords'):
            self.compare_list(lnode.keywords, rnode.keywords)

        if hasattr(lnode, 'starargs'):
            self.compare(lnode.starargs, rnode.starargs)
            self.compare(lnode.kwargs, rnode.kwargs)

        self.compare_list(lnode.decorator_list, rnode.decorator_list)
        self.compare_list(lnode.body, rnode.body)

        self.namespaces.pop()

    # endregion

    # region async and await

    def compare_AsyncFunctionDef(self, lnode, rnode):
        if lnode.name != rnode.name:
            raise CompareError(self.namespaces, lnode, rnode, 'AsyncFunctionDef names do not match')

        self.namespaces.append(lnode.name)

        self.compare(lnode.args, rnode.args)
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.decorator_list, rnode.decorator_list)
        self.compare(lnode.returns, rnode.returns)

        self.namespaces.pop()

    def compare_Await(self, lnode, rnode):
        self.compare(lnode.value, rnode.value)

    def compare_AsyncFor(self, lnode, rnode):
        self.compare(lnode.target, rnode.target)
        self.compare(lnode.iter, rnode.iter)
        self.compare_list(lnode.body, rnode.body)
        self.compare_list(lnode.orelse, rnode.orelse)

    def compare_AsyncWith(self, lnode, rnode):

        if hasattr(lnode, 'items'):
            self.compare_list(lnode.items, rnode.items)
        else:
            self.compare(lnode.context_expr, rnode.context_expr)
            self.compare(lnode.optional_vars, rnode.optional_vars)

    # endregion

    def compare_Module(self, lnode, rnode):
        self.compare_list(lnode.body, rnode.body)
