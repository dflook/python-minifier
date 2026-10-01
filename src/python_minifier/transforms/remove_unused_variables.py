import python_minifier.ast_compat as ast

from python_minifier.transforms.scope_analysis import DeadCodeTransformer
from python_minifier.transforms.side_effects import is_side_effect_free


class RemoveUnusedVariables(DeadCodeTransformer):
    """
    Remove assignments to variables that are never used

    Only assignments of a single name are removed, and only when the assigned value is known to have no side effects.
    """

    def eliminate(self, node):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            annotation = None
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target = node.target
            annotation = node.annotation
        else:
            return node

        if not isinstance(target, ast.Name):
            return node

        if not is_side_effect_free(node.value) or not is_side_effect_free(annotation):
            return node

        if not self.scope.is_removable(target, target.id):
            return node

        self.changed = True
        return None
