import ast

from python_minifier.rename.mapper import add_parent


class NodeVisitor(object):
    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)

    def visit_Constant(self, node):
        if node.value in [None, True, False]:
            method = 'visit_NameConstant'
        elif isinstance(node.value, (int, float, complex)):
            method = 'visit_Num'
        elif isinstance(node.value, str):
            method = 'visit_Str'
        elif isinstance(node.value, bytes):
            method = 'visit_Bytes'
        elif node.value == Ellipsis:
            method = 'visit_Ellipsis'
        else:
            raise RuntimeError('Unknown Constant value %r' % type(node.value))

        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def is_node(self, node, types):
        """
        Is a node one of the specified node types

        A node type may be an actual ast class, or a string naming one.
        types is a single node type or an iterable of many.

        If a node_type specified a specific Constant type (Str, Bytes, Num etc),
        returns true for Constant nodes of the correct type.

        :type node: ast.AST
        :param types:
        :rtype: bool

        """

        if not isinstance(types, tuple):
            types = (types,)

        actual_types = []
        for node_type in types:
            if isinstance(node_type, str):
                node_type = getattr(ast, node_type, None)
                if node_type is not None:
                    actual_types.append(node_type)
            else:
                actual_types.append(node_type)

        if isinstance(node, tuple(actual_types)):
            return True

        if hasattr(ast, 'Constant') and isinstance(node, ast.Constant):
            if node.value in [None, True, False]:
                return ast.NameConstant in types
            elif isinstance(node.value, (int, float, complex)):
                return ast.Num in types
            elif isinstance(node.value, str):
                return ast.Str in types
            elif isinstance(node.value, bytes):
                return ast.Bytes in types
            elif node.value == Ellipsis:
                return ast.Ellipsis in types
            else:
                raise RuntimeError('Unknown Constant value %r' % type(node.value))

        return False


class SuiteTransformer(NodeVisitor):
    """
    Transform suites of instructions
    """

    def __call__(self, node):
        return self.visit(node)

    def visit_ClassDef(self, node):
        node.bases = [self.visit(b) for b in node.bases]

        node.body = self.suite(node.body, parent=node)
        node.decorator_list = [self.visit(d) for d in node.decorator_list]

        if hasattr(node, 'starargs') and node.starargs is not None:
            node.starargs = self.visit(node.starargs)

        if hasattr(node, 'kwargs') and node.kwargs is not None:
            node.kwargs = self.visit(node.kwargs)

        if hasattr(node, 'keywords'):
            node.keywords = [self.visit(kw) for kw in node.keywords]

        return node

    def visit_FunctionDef(self, node):
        node.args = self.visit(node.args)
        node.body = self.suite(node.body, parent=node)
        node.decorator_list = [self.visit(d) for d in node.decorator_list]

        if hasattr(node, 'returns') and node.returns is not None:
            node.returns = self.visit(node.returns)

        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_For(self, node):
        node.target = self.visit(node.target)
        node.iter = self.visit(node.iter)

        node.body = self.suite(node.body, parent=node)

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        return node

    def visit_AsyncFor(self, node):
        return self.visit_For(node)

    def visit_If(self, node):
        node.test = self.visit(node.test)

        node.body = self.suite(node.body, parent=node)

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        return node

    def visit_Try(self, node):
        node.body = self.suite(node.body, parent=node)

        node.handlers = [self.visit(h) for h in node.handlers]

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        if node.finalbody:
            node.finalbody = self.suite(node.finalbody, parent=node)

        return node

    def visit_While(self, node):
        node.test = self.visit(node.test)

        node.body = self.suite(node.body, parent=node)

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        return node

    def visit_With(self, node):

        if hasattr(node, 'items'):
            node.items = [self.visit(i) for i in node.items]
        else:
            if node.context_expr:
                node.context_expr = self.visit(node.context_expr)
            if node.optional_vars:
                node.optional_vars = self.visit(node.optional_vars)

        node.body = self.suite(node.body, parent=node)
        return node

    def visit_AsyncWith(self, node):
        return self.visit_With(node)

    def visit_Module(self, node):
        node.body = self.suite(node.body, parent=node)
        return node

    def suite(self, node_list, parent):
        return [self.visit(node) for node in node_list]

    def generic_visit(self, node):
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def add_child(self, child, parent, namespace=None):
        def nearest_function_namespace(node):
            """
            Return the namespace node for the nearest function scope.

            This could be itself.

            :param node: The node to get the function namespace of
            :type node: ast.Node
            :rtype: ast.Node

            """

            if isinstance(node, (ast.FunctionDef, ast.Module)):
                return node
            if hasattr(ast, 'AsyncFunctionDef') and isinstance(node, ast.AsyncFunctionDef):
                return node
            return nearest_function_namespace(node.parent)

        if namespace is None:
            namespace = nearest_function_namespace(parent)

        add_parent(child, parent=parent, namespace=namespace)
        return child
