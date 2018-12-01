import ast


def find_doc(node):

    if isinstance(node, ast.Attribute):
        if node.attr == '__doc__':
            raise ValueError('__doc__ found!')

    for child in ast.iter_child_nodes(node):
        find_doc(child)


def _doc_in_module(module):
    try:
        find_doc(module)
        return False
    except:
        return True

class RemoveLiteralStatements(ast.NodeTransformer):
    """
    Remove literal expressions from the code

    This includes docstrings
    """

    def __call__(self, node):
        if _doc_in_module(node):
            return node
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
        for binding in node.bindings:
            if binding.name == '__doc__':
                node.body = [self.visit(a) for a in node.body]
                return node

        node.body = self.suite(node.body, module=True)
        return node

    def is_literal_statement(self, node):
        if not isinstance(node, ast.Expr):
            return False

        if (
            isinstance(node.value, ast.Num)
            or isinstance(node.value, ast.Str)
            or node.value.__class__.__name__ == 'Bytes'
        ):
            return True

        return False

    def suite(self, node_list, module=False):
        without_literals = [self.visit(a) for a in filter(lambda n: not self.is_literal_statement(n), node_list)]

        if len(without_literals) == 0:
            if module:
                return []
            else:
                return [ast.Expr(value=ast.Num(0))]

        return without_literals
