import ast

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

class SuiteTransformer(NodeVisitor):
    """
    Transform suites of instructions
    """

    def __call__(self, node):
        return self.visit(node)

    def visit_ClassDef(self, node):
        node.body = self.suite(node.body, parent=node)
        return node

    def visit_FunctionDef(self, node):
        node.body = self.suite(node.body, parent=node)
        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_For(self, node):
        node.body = self.suite(node.body, parent=node)

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        return node

    def visit_AsyncFor(self, node):
        node.body = self.suite(node.body, parent=node)

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        return node

    def visit_If(self, node):
        node.body = self.suite(node.body, parent=node)
        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        return node

    def visit_Try(self, node):
        node.body = self.suite(node.body, parent=node)

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        if node.finalbody:
            node.finalbody = self.suite(node.finalbody, parent=node)

        return node

    def visit_While(self, node):
        node.body = self.suite(node.body, parent=node)

        if node.orelse:
            node.orelse = self.suite(node.orelse, parent=node)

        return node

    def visit_With(self, node):
        node.body = self.suite(node.body, parent=node)
        return node

    def visit_AsyncWith(self, node):
        node.body = self.suite(node.body, parent=node)
        return node

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
