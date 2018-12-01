import ast


class CombineImports(ast.NodeTransformer):
    """
    Combine multiple import statements where possible

    This doesn't change the order of imports

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
        node.body = self.suite(node.body)
        return node

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
        node.body = self.suite(node.body)
        return node

    def visit_Module(self, node):
        node.body = self.suite(node.body)
        return node

    def _combine_import(self, node_list):

        alias = []

        for statement in node_list:
            if isinstance(statement, ast.Import):
                alias += statement.names
            else:
                if alias:
                    yield ast.Import(names=alias)
                    alias = []

                yield statement

        if alias:
            yield ast.Import(names=alias)

    def _combine_import_from(self, node_list):

        prev_import = None
        alias = []

        def combine(statement):
            if not isinstance(statement, ast.ImportFrom):
                return False

            if len(statement.names) == 1 and statement.names[0].name == '*':
                return False

            if prev_import is None:
                return True

            if statement.module == prev_import.module and statement.level == prev_import.level:
                return True

            return False

        for statement in node_list:
            if combine(statement):
                prev_import = statement
                alias += statement.names
            else:
                if alias:
                    yield ast.ImportFrom(module=prev_import.module, names=alias, level=prev_import.level)
                    alias = []

                yield statement

        if alias:
            yield ast.ImportFrom(module=prev_import.module, names=alias, level=prev_import.level)

    def suite(self, node_list):
        a = list(self._combine_import(node_list))
        b = list(self._combine_import_from(a))

        return [self.visit(n) for n in b]
