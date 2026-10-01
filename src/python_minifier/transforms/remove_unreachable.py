import python_minifier.ast_compat as ast

from python_minifier.transforms.remove_dead_branches import in_function_scope
from python_minifier.transforms.scope_analysis import DeadCodeTransformer, makes_local

_TRY = tuple(getattr(ast, name) for name in ('Try', 'TryExcept', 'TryFinally') if hasattr(ast, name))


def _suite_terminates(suite, raises):
    return bool(suite) and _terminates(suite[-1], raises)


def _terminates(node, raises=True):
    """
    Does control never continue to the statement after this one?

    :param node: The statement to check
    :type node: ast.AST
    :param bool raises: If a ``raise`` statement counts as terminating
    :rtype: bool
    """

    if isinstance(node, (ast.Return, ast.Break, ast.Continue)):
        return True

    if isinstance(node, ast.Raise):
        return raises

    if isinstance(node, ast.If):
        return bool(node.orelse) and _suite_terminates(node.body, raises) and _suite_terminates(node.orelse, raises)

    if isinstance(node, ast.TryStar):
        return _suite_terminates(node.finalbody, raises)

    if isinstance(node, _TRY):
        if _suite_terminates(getattr(node, 'finalbody', []), raises):
            return True

        if not (_suite_terminates(node.body, raises) or _suite_terminates(getattr(node, 'orelse', []), raises)):
            return False

        return all(_suite_terminates(handler.body, raises) for handler in getattr(node, 'handlers', []))

    if isinstance(node, (ast.With, ast.AsyncWith)):
        # The context manager can suppress an exception raised in the body
        return _suite_terminates(node.body, raises=False)

    # Loops may never run their body, and the else clause of a loop runs when it is not broken out of
    return False


class RemoveUnreachable(DeadCodeTransformer):
    """
    Remove statements that follow a statement that always return, raises, breaks or continues

    Statements are kept if removing them would change the meaning of the program, for example if
    they contain a ``yield`` or the only assignment to a local variable that is used earlier.
    """

    def suite(self, node_list, parent):
        reachable = []

        for index, node in enumerate(node_list):
            reachable.append(self.visit(node))

            unreachable = node_list[index + 1:]
            if unreachable and _terminates(node) and self.can_remove(unreachable):
                self.changed = True
                break

        return reachable

    def can_remove(self, statements):
        """
        Can these statements be removed without changing the meaning of the enclosing scope?

        :param list statements: Consecutive statements in a suite
        :rtype: bool
        """

        namespace = statements[0].namespace
        nodes = [node for statement in statements for node in ast.walk(statement)]

        for node in nodes:
            if isinstance(node, (ast.Yield, ast.YieldFrom, ast.Global, ast.Nonlocal)) and getattr(node, 'namespace', None) is namespace:
                return False

        if isinstance(namespace, ast.Module) or (isinstance(namespace, ast.ClassDef) and not in_function_scope(namespace)):
            # Name resolution is dynamic in these scopes
            return True

        removed = {id(node) for node in nodes}
        local_bindings = {id(binding) for binding in namespace.bindings}

        for node in nodes:
            if getattr(node, 'namespace', None) is not namespace or not makes_local(node):
                continue

            binding = self.scope.binding(node)
            if binding is None:
                continue

            if isinstance(namespace, ast.ClassDef):
                # A class body binding hides the enclosing function's name from loads in the class body only
                references = [reference for reference in binding.references if getattr(reference, 'namespace', None) is namespace]
            elif id(binding) in local_bindings:
                references = binding.references
            else:
                continue

            # Without these statements the name would no longer be local to this namespace
            remaining = [reference for reference in references if id(reference) not in removed]
            if remaining and not any(makes_local(reference) for reference in remaining):
                return False

        return True
