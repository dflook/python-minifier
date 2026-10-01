import python_minifier.ast_compat as ast

from python_minifier.transforms.scope_analysis import DeadCodeTransformer
from python_minifier.transforms.side_effects import is_definition_side_effect_free


class RemoveUnusedDefinitions(DeadCodeTransformer):
    """
    Remove function and class definitions that are never used

    Decorated definitions are never removed, as the decorator may register the definition somewhere.
    Neither are definitions that evaluate something with side effects when they are executed.
    """

    def eliminate(self, node):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return node

        if not is_definition_side_effect_free(node) or not self.scope.is_removable(node, node.name):
            return node

        self.changed = True
        return None
