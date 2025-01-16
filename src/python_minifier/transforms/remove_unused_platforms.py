import ast

from python_minifier.transforms.remove_unused_platform_options import (
    RemoveUnusedPlatformOptions,
)
from python_minifier.transforms.suite_transformer import SuiteTransformer


class RemoveUnusedPlatforms(SuiteTransformer):
    """
    Remove if statements where the condition tests a platform check if statement

    If a statement is syntactically necessary, use an empty expression instead

    Modelled off the __debug__ test.  If this needs extending, then that is a
    good example.
    """

    def __init__(self, options):
        assert isinstance(options, RemoveUnusedPlatformOptions)
        self._options = options
        super(RemoveUnusedPlatforms, self).__init__()

    def __call__(self, node):
        return self.visit(node)

    @staticmethod
    def is_single_equal_explicit_if_comparison(node):
        """
        Is this a simple single operator, such as `left == 'right'`
        """

        return (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.Eq)
            and len(node.test.comparators) == 1
        )

    def split_platform_tests(self, node):
        """
        Returns None if this is an unrelated or unsupported statement.

        Otherwise, returns a tuple with the following elements:

            A list of matching `if PLATFORM == Target:` nodes
            A list of matching `if PLATFORM == NonTarget:` nodes
            The open else nodes
        """
        if not self.is_single_equal_explicit_if_comparison(node):
            return None

        # Collect if node with multiple elif nodes
        comparisons = []
        open_else_nodes = []
        current_node = node
        while current_node is not None:
            if not self.is_single_equal_explicit_if_comparison(current_node):
                return None
            comparisons.append(current_node)
            if current_node.orelse:
                if isinstance(current_node.orelse[0], ast.If):
                    # elif
                    current_node = current_node.orelse[0]
                else:
                    # else body
                    open_else_nodes = current_node.orelse
                    current_node = None
            else:
                current_node = None

        matching_platform_test = []
        unmatched_platform_test = []
        other_tests = []

        # Check each if statement for a platform match:
        for if_comparison in comparisons:
            test_key = None
            test_value = None
            left = if_comparison.test.left
            if isinstance(left, ast.Constant):
                test_value = left.value
            elif isinstance(left, ast.Name):
                test_key = left.id

            comparator = if_comparison.test.comparators[0]
            if isinstance(comparator, ast.Constant):
                test_value = comparator.value
            elif isinstance(comparator, ast.Name):
                test_key = comparator.id

            if test_key == self._options.platform_test_key:
                if test_value == self._options.platform_preserve_value:
                    matching_platform_test.append(if_comparison)
                else:
                    unmatched_platform_test.append(if_comparison)
            else:
                other_tests.append(if_comparison)

        if other_tests:
            return None

        return matching_platform_test, unmatched_platform_test, open_else_nodes

    def can_remove(self, node):
        target_test = self.split_platform_tests(node)
        if target_test is None:
            # No target tests, do not remove node
            return False
        elif target_test[1] and not target_test[0] and not target_test[2]:
            # Only non-target platforms specified, can be removed
            return True
        else:
            # Keep everything else
            return False

    def flattened_node(self, node):
        """
        Returns a modified node if the existing node can be flattened or removed.  NOOP nodes
        are returned as None.
        """
        if isinstance(node, ast.Pass) or node == ast.Num(0):
            return None

        target_split_nodes = self.split_platform_tests(node)
        if target_split_nodes:
            (
                matching_platform_test,
                unmatched_platform_test,
                open_else_nodes,
            ) = target_split_nodes

            if not matching_platform_test and open_else_nodes:
                matching_platform_bodies = [open_else_nodes]
            else:
                matching_platform_bodies = [n.body for n in matching_platform_test]

            combined_bodies = []

            for m in matching_platform_bodies:
                if len(m) == 1 and (isinstance(m[0], ast.Pass) or m[0] == ast.Num(0)):
                    pass
                else:
                    combined_bodies += m

            return combined_bodies

        return node

    def suite(self, node_list, parent):
        if not isinstance(parent, ast.Module):
            return node_list

        # Logical Parse of the tree
        without_unused_platform = [
            self.visit(a) for a in filter(lambda _n: not self.can_remove(_n), node_list)
        ]

        # Clean up remaining NOOP statements or blocks
        flattened_nodes = []
        for n in without_unused_platform:
            processed_n = self.flattened_node(n)
            if isinstance(processed_n, list):
                flattened_nodes += processed_n
            elif processed_n:
                flattened_nodes.append(processed_n)

        if len(flattened_nodes) == 0:
            return []

        return flattened_nodes
