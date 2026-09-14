import python_minifier.ast_compat as ast

from python_minifier.transforms.suite_transformer import SuiteTransformer


def import_kwargs(import_node):
    lazy = getattr(import_node, 'is_lazy', None)
    if lazy is None:
        return {}
    return {'is_lazy': lazy}


class CombineImports(SuiteTransformer):
    """
    Combine multiple import statements where possible

    This doesn't change the order of imports

    """

    def _combine_import(self, node_list, parent):

        prev_import = None
        alias = []

        def can_merge_with_previous_group(statement):
            if not isinstance(statement, ast.Import):
                return False

            if prev_import is None:
                return True

            if getattr(statement, 'is_lazy', None) != getattr(prev_import, 'is_lazy', None):
                return False

            return True

        def can_create_group(statement):
            return isinstance(statement, ast.Import)

        for statement in node_list:
            if can_merge_with_previous_group(statement):
                prev_import = statement
                alias += statement.names
            else:
                if alias:
                    yield self.add_child(ast.Import(names=alias, **import_kwargs(prev_import)), parent=parent, namespace=prev_import.namespace)
                    prev_import = None
                    alias = []

                if can_create_group(statement):
                    prev_import = statement
                    alias += statement.names
                else:
                    yield statement

        if alias:
            yield self.add_child(ast.Import(names=alias, **import_kwargs(prev_import)), parent=parent, namespace=prev_import.namespace)

    def _combine_import_from(self, node_list, parent):

        prev_import = None
        alias = []

        def can_merge_with_previous_group(statement):
            if not isinstance(statement, ast.ImportFrom):
                return False

            if len(statement.names) == 1 and statement.names[0].name == '*':
                return False

            if prev_import is None:
                return True

            if getattr(statement, 'is_lazy', None) != getattr(prev_import, 'is_lazy', None):
                return False

            if statement.module == prev_import.module and statement.level == prev_import.level:
                return True

            return False

        def can_create_group(statement):
            if not isinstance(statement, ast.ImportFrom):
                return False

            if len(statement.names) == 1 and statement.names[0].name == '*':
                return False

            return True

        for statement in node_list:
            if can_merge_with_previous_group(statement):
                prev_import = statement
                alias += statement.names
            else:
                if alias:
                    yield self.add_child(
                        ast.ImportFrom(module=prev_import.module, names=alias, level=prev_import.level, **import_kwargs(prev_import)), parent=parent, namespace=prev_import.namespace
                    )
                    prev_import = None
                    alias = []

                if can_create_group(statement):
                    prev_import = statement
                    alias += statement.names
                else:
                    yield statement

        if alias:
            yield self.add_child(
                ast.ImportFrom(module=prev_import.module, names=alias, level=prev_import.level, **import_kwargs(prev_import)), parent=parent, namespace=prev_import.namespace
            )

    def suite(self, node_list, parent):
        a = list(self._combine_import(node_list, parent))
        b = list(self._combine_import_from(a, parent))

        return [self.visit(n) for n in b]
