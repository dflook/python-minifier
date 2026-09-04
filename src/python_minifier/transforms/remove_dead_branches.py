import python_minifier.ast_compat as ast

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
        Gather the binding properties of a namespace

        Walks the namespace and collects the names it binds (as local, nonlocal
        and global name sets) and whether it is a generator.

        :param namespace: The namespace node to analyse
        :param removed_suites: Suites to skip while walking, for
            branches that are being removed.
        :type removed_suites: list or None
        :rtype: NamespaceProperties
        """
        if removed_suites is None:
            removed_suites = []

        properties = NamespaceProperties()

        def explore_namespace(node):
            binds_here = getattr(node, 'namespace', namespace) is namespace

            if binds_here:
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, (ast.Store, ast.Del, ast.Param)):
                        properties.local_names.add(node.id)
                elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
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

                elif isinstance(node, (ast.Yield, ast.YieldFrom)):
                    properties.is_generator = True

            # Skip recursing into the body field of child namespaces, as they can only affect the child namespace
            # Other fields (decorators, annotations, arguments...) can affect this namespace,
            # so we do want to recurse into them
            skip_body = node is not namespace and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))

            for name, field in ast.iter_fields(node):
                if field in removed_suites:
                    continue

                if skip_body and name == 'body':
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

        declarations_changed = (
            properties.is_generator != candidate_properties.is_generator
            or properties.nonlocal_names != candidate_properties.nonlocal_names
            or properties.global_names != candidate_properties.global_names
        )

        if isinstance(namespace, ast.Module):
            # The module namespace is dynamic, removing unreachable bindings doesn't
            # change their resolution behaviour, so we can safely remove them.
            return declarations_changed
        elif isinstance(namespace, ast.ClassDef) and not in_function_scope(namespace):
            # Class namespaces are also dynamic, but a binding in the class body stops
            # loads deferring to an enclosing function scope cell, so unreachable local
            # bindings can only be ignored when no function scope encloses the class.
            return declarations_changed
        else:
            return properties != candidate_properties

    def constant_test(self, node):
        """
        The constant truth value of an if statement's test, or None

        RemoveDebug marks if statements whose __debug__ test it has resolved
        with a resolved_test attribute. Otherwise only the True and False
        constants are recognised - before python 3.4 they are reassignable
        names, so nothing is recognised.

        :param node: The statement to examine
        :type node: ast.AST
        :rtype: bool or None
        """
        if not isinstance(node, ast.If):
            return None

        if hasattr(node, 'resolved_test'):
            if node.resolved_test is True or node.resolved_test is False:
                return node.resolved_test
            return None

        if is_constant_node(node.test, ast.NameConstant) and isinstance(node.test.value, bool):
            return node.test.value

        return None

    def remove_false_branches(self, node_list):
        suite = []

        for node in node_list:
            condition = self.constant_test(node)

            # A branch of a constant test can be removed, if that doesn't change
            # the semantics of the program

            if condition is True and not self.changes_semantics(node.namespace, node.orelse):
                # The else branch is dead, keep only the body
                self._removed_suites.append(node.orelse)
                suite.extend(self.remove_false_branches(node.body))
                continue

            if condition is False and not self.changes_semantics(node.namespace, node.body):
                # The body is dead, keep only the else branch
                self._removed_suites.append(node.body)
                suite.extend(self.remove_false_branches(node.orelse))
                continue

            node = self.visit(node)

            # An else suite that dead branch removal (or another transform) emptied
            # or reduced to the 0 padding can be omitted.
            orelse = getattr(node, 'orelse', None)
            if orelse and self._is_empty_suite(orelse):
                node.orelse = []

            suite.append(node)

        return suite

    def suite(self, node_list, parent):

        without_dead_branches = self.remove_false_branches(node_list)

        if len(without_dead_branches) == 0:
            if isinstance(parent, ast.Module):
                return []
            else:
                return [self.add_child(ast.Expr(value=ast.Num(0)), parent=parent)]

        return without_dead_branches

    def _is_empty_suite(self, suite):
        """
        Is the suite empty?

        An empty suite is either a zero length list, or a list containing a single expression statement that is the constant 0.
        The constant 0 is used by various transforms as a placeholder for an empty suite, because not all suites can be empty (e.g. the body of a function or class).

        :param suite:
        :type suite: list
        :rtype: bool
        """
        if len(suite) == 0:
            return True
        return len(suite) == 1 and isinstance(suite[0], ast.Expr) and is_constant_node(suite[0].value, ast.Num) and suite[0].value.n == 0
