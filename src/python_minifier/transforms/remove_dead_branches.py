import python_minifier.ast_compat as ast
from python_minifier.rename.util import is_namespace

from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_constant_node

class NamespaceProperties(object):
    """
    The analysed properties of a namespace, including the names defined in it and whether it is a generator
    """

    def __init__(self):
        self.local_names = set()
        self.nonlocal_names = set()
        self.global_names = set()
        self.is_generator = False

    def __eq__(self, other):
        assert isinstance(other, NamespaceProperties)
        return (
            self.local_names == other.local_names and
            self.nonlocal_names == other.nonlocal_names and
            self.global_names == other.global_names and
            self.is_generator is other.is_generator
        )

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'NamespaceProperties(local_names=%r, nonlocal_names=%r, global_names=%r, is_generator=%r)' % (
            self.local_names, self.nonlocal_names, self.global_names, self.is_generator
        )


def in_function_scope(namespace):
    """
    Is this namespace nested in a function scope?

    A name bound anywhere in a class body - even in unreachable code - makes
    loads of that name in the class body fall through to the global scope,
    instead of an enclosing function scope cell. Removing such a binding is
    only safe when there is no enclosing function scope to fall through to.
    """
    while not isinstance(namespace, ast.Module):
        if isinstance(namespace, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return True
        namespace = namespace.namespace
    return False


class RemoveDeadBranches(SuiteTransformer):
    """
    Remove if statements where the condition tests False
    """

    def __call__(self, node):
        # Suites that have been condemned during this run, but may not have been
        # detached from the tree yet. Shared across all suites so that decisions
        # in nested or sibling suites don't count already-removed bindings.
        self._removed_suites = []
        return self.visit(node)

    def get_namespace_properties(self, namespace, removed_suites=None):
        """
        Gather names in the given namespace

        Gather three sets of names: local, nonlocal and global.

        Doesn't recurse into child namespaces, and doesn't search the except_suite, which is assumed to be a branch that will be removed.

        :param namespace:
        :param except_branch:
        :rtype: set[str]
        """
        if removed_suites is None:
            removed_suites = []

        properties = NamespaceProperties()

        def explore_namespace(node):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, (ast.Store, ast.Del, ast.Param)):
                    properties.local_names.add(node.id)
            elif isinstance(node, ast.ClassDef):
                properties.local_names.add(node.name)
            elif isinstance(node, ast.FunctionDef):
                properties.local_names.add(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                properties.local_names.add(node.name)
            elif isinstance(node, ast.alias):
                # What about import *

                if node.asname is not None:
                    properties.local_names.add(node.asname)
                else:
                    properties.local_names.add(node.name.split('.')[0])
            elif isinstance(node, ast.arguments):
                if isinstance(node.vararg, str):
                    properties.local_names.add(node.vararg)
                if isinstance(node.kwarg, str):
                    properties.local_names.add(node.kwarg)
            elif isinstance(node, ast.arg):
                properties.local_names.add(node.arg)
            elif isinstance(node, ast.ExceptHandler):
                if isinstance(node.name, str):
                    properties.local_names.add(node.name)

            elif isinstance(node, ast.Global):
                properties.global_names.update(node.names)
            elif isinstance(node, ast.Nonlocal):
                properties.nonlocal_names.update(node.names)

            elif isinstance(node, ast.MatchAs):
                if isinstance(node.name, str):
                    properties.local_names.add(node.name)
            elif isinstance(node, ast.MatchStar):
                if isinstance(node.name, str):
                    properties.local_names.add(node.name)
            elif isinstance(node, ast.MatchMapping):
                if isinstance(node.rest, str):
                    properties.local_names.add(node.rest)

            elif isinstance(node, ast.TypeVar):
                properties.local_names.add(node.name)
            elif isinstance(node, ast.TypeVarTuple):
                properties.local_names.add(node.name)
            elif isinstance(node, ast.ParamSpec):
                properties.local_names.add(node.name)

            elif isinstance(node, ast.Yield) or isinstance(node, ast.YieldFrom):
                properties.is_generator = True

            if is_namespace(node) and node is not namespace:
                # A nested namespace. The name it binds (recorded above) belongs to
                # this namespace, but its contents do not - don't descend into it.
                return

            for name, field in ast.iter_fields(node):
                if field in removed_suites:
                    continue

                if isinstance(field, ast.AST):
                    explore_namespace(field)
                elif isinstance(field, list):
                    for item in field:
                        if isinstance(item, ast.AST):
                            explore_namespace(item)

        explore_namespace(namespace)

        return properties

    def changes_semantics(self, namespace, candidate_suite):
        """
        Does removing this branch change the semantics of the program?

        :param namespace: The namespace of the If statement
        :param candidate_suite: The branch that is being removed
        :return: True if removing the branch changes the semantics of the program, False otherwise
        """

        # Gather properties in the namespace, excluding suites already condemned
        properties = self.get_namespace_properties(namespace, removed_suites=self._removed_suites)

        # Gather properties in the namespace, additionally excluding the candidate branch
        candidate_properties = self.get_namespace_properties(namespace, removed_suites=[candidate_suite] + self._removed_suites)

        if isinstance(namespace, ast.Module):
            # The module namespace is dynamic, removing unreachable bindings doesn't
            # change their resolution behaviour, so we can safely remove them.
            return properties.is_generator != candidate_properties.is_generator or properties.nonlocal_names != candidate_properties.nonlocal_names or properties.global_names != candidate_properties.global_names
        elif isinstance(namespace, ast.ClassDef) and not in_function_scope(namespace):
            # Class namespaces are also dynamic, but a binding in the class body stops
            # loads deferring to an enclosing function scope cell, so unreachable local
            # bindings can only be ignored when no function scope encloses the class.
            return properties.is_generator != candidate_properties.is_generator or properties.nonlocal_names != candidate_properties.nonlocal_names or properties.global_names != candidate_properties.global_names
        else:
            return properties != candidate_properties

    def remove_false_branches(self, node_list):
        suite = []

        for node in node_list:
            if not isinstance(node, ast.If):
                suite.append(self.visit(node))
                continue

            # This is an If statement

            if hasattr(node, 'resolved_test'):
                condition = node.resolved_test
            elif is_constant_node(node.test, ast.NameConstant) and isinstance(node.test.value, bool):
                condition = node.test.value
            else:
                # The test is not a constant, so we can't remove this branch
                suite.append(self.visit(node))
                continue

            # We can possibly remove one of the branches, but we need to check if it changes the semantics of the program

            if condition is True:
                if self.changes_semantics(node.namespace, node.orelse):
                    # Removing the else branch changes the semantics of the program, so we can't remove it
                    suite.append(self.visit(node))
                else:
                    # The else branch is dead, keep only the body
                    self._removed_suites.append(node.orelse)
                    suite.extend(self.remove_false_branches(node.body))

            elif condition is False:
                if self.changes_semantics(node.namespace, node.body):
                    # Removing the body branch changes the semantics of the program, so we can't remove it
                    suite.append(self.visit(node))
                else:
                    # The body is dead, keep only the else branch
                    self._removed_suites.append(node.body)
                    suite.extend(self.remove_false_branches(node.orelse))

        return suite

    def suite(self, node_list, parent):

        without_dead_branches = self.remove_false_branches(node_list)

        if len(without_dead_branches) == 0:
            if isinstance(parent, ast.Module):
                return []
            else:
                return [self.add_child(ast.Expr(value=ast.Num(0)), parent=parent)]

        return without_dead_branches
