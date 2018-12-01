import ast


class RemovePass(ast.NodeTransformer):
    """
    Remove Pass keywords from source

    If a statement is syntactically necessary, use an empty expression instead
    """

    def __call__(self, node):
        return self.visit(node)

    def visit_ClassDef(self, node):
        node.body = self.suite(node.body)
        return node

    def visit_FunctionDef(self, node):
        node.body = self.suite(node.body)
        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_For(self, node):
        node.body = self.suite(node.body)

        if node.orelse:
            node.orelse = self.suite(node.orelse)

        return node

    def visit_AsyncFor(self, node):
        return self.visit_For(node)

    def visit_If(self, node):
        node.body = self.suite(node.body)
        if node.orelse:
            node.orelse = self.suite(node.orelse)

        return node

    def visit_Try(self, node):
        node.body = self.suite(node.body)

        if node.orelse:
            node.orelse = self.suite(node.orelse)

        if node.finalbody:
            node.finalbody = self.suite(node.finalbody)

        return node

    def visit_While(self, node):
        node.body = self.suite(node.body)

        if node.orelse:
            node.orelse = self.suite(node.orelse)

        return node

    def visit_With(self, node):
        node.body = self.suite(node.body)
        return node

    def visit_AsyncWith(self, node):
        return self.visit_With(node)

    def visit_Module(self, node):
        node.body = self.suite(node.body, module=True)
        return node

    def suite(self, node_list, module=False):
        without_pass = [self.visit(a) for a in filter(lambda n: not isinstance(n, ast.Pass), node_list)]

        if len(without_pass) == 0:
            if module:
                return []
            else:
                return [ast.Expr(value=ast.Num(0))]

        return without_pass
