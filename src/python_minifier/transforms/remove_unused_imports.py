import python_minifier.ast_compat as ast

from python_minifier.transforms.scope_analysis import DeadCodeTransformer


class RemoveUnusedImports(DeadCodeTransformer):
    """
    Remove imported names that are never used

    An import statement is removed when none of the names it binds are used. If only some of them are unused,
    only those names are removed from the statement.

    ``__future__`` imports are never removed.
    """

    def eliminate(self, node):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            return node

        if isinstance(node, ast.ImportFrom) and node.module == '__future__':
            return node

        used = [alias for alias in node.names if not self.is_unused(alias)]
        if len(used) == len(node.names):
            return node

        self.changed = True

        if not used:
            return None

        node.names = used
        return node

    def is_unused(self, alias):
        if alias.name == '*':
            return False

        # A dotted import without an alias binds only the root package
        name = alias.asname or alias.name.split('.')[0]

        return self.scope.is_removable(alias, name)
