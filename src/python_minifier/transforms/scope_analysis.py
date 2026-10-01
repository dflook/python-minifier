import python_minifier.ast_compat as ast
from python_minifier.ast_annotation import get_parent
from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_constant_node


def is_dunder_name(name):
    """
    Is this a name like __init__, which has a special meaning to python

    :param str name: The name to check
    :rtype: bool
    """

    return name.startswith('__') and name.endswith('__')


def reads_name(reference):
    """
    Does a reference to a binding use the current value of the name?

    A binding that is only referenced by the statements that define it is never used.
    Anything else that mentions the name counts as a use, including ``del`` statements,
    augmented assignments and ``global`` or ``nonlocal`` declarations, which let other
    scopes read and write the name.

    :param reference: A node from the references of a binding
    :type reference: ast.AST
    :rtype: bool
    """

    if isinstance(reference, ast.Name):
        if isinstance(reference.ctx, (ast.Load, ast.Del)):
            return True

        if isinstance(reference.ctx, ast.Store):
            try:
                return isinstance(get_parent(reference), ast.AugAssign)
            except ValueError:
                return True

        return False

    return isinstance(reference, (ast.Global, ast.Nonlocal))


def makes_local(reference):
    """
    Does a reference to a binding cause the name to be local to its namespace?

    :param reference: A node from the references of a binding
    :type reference: ast.AST
    :rtype: bool
    """

    if isinstance(reference, ast.Name):
        return not isinstance(reference.ctx, ast.Load)

    return not isinstance(reference, (ast.Global, ast.Nonlocal))


def find_exports(module):
    """
    Find the names a module lists in ``__all__``

    :param module: The module to search
    :type module: ast.Module
    :return: The listed names, or None if ``__all__`` is used in a way that can't be determined statically
    :rtype: set[str] or None
    """

    names = set()

    for node in ast.walk(module):
        if isinstance(node, ast.Name) and node.id == '__all__' and isinstance(node.ctx, ast.Load):
            return None

        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        else:
            continue

        if not any(isinstance(target, ast.Name) and target.id == '__all__' for target in targets):
            continue

        if node.value is None:
            continue

        if not isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
            return None

        for element in node.value.elts:
            if not is_constant_node(element, ast.Str):
                return None
            names.add(element.s)

    return names


class ScopeAnalysis(object):
    """
    Answers questions about how names are used in a module

    The module must have had its names bound and resolved, the analysis is invalid once
    the module is changed.

    :param module: The module to analyse
    :type module: ast.Module
    """

    def __init__(self, module):
        self._binding_for_reference = {}

        for node in ast.walk(module):
            for binding in getattr(node, 'bindings', ()):
                for reference in binding.references:
                    self._binding_for_reference[id(reference)] = binding

        self._exports = find_exports(module)

    def binding(self, node):
        """
        The binding that a node creates or references

        :type node: ast.AST
        :rtype: python_minifier.rename.binding.NameBinding or None
        """

        return self._binding_for_reference.get(id(node))

    def is_removable(self, node, name):
        """
        Can the statement that makes a node bind a name be removed, as far as the name is concerned?

        The name must never be used in the module. Names that could be used from outside the
        module, or that the interpreter gives a meaning to, are never unused. Class namespaces
        are skipped as the names in them become attributes of the class.

        :param node: The node that binds the name. This is a Name, alias, FunctionDef, AsyncFunctionDef or ClassDef
        :type node: ast.AST
        :param str name: The name being bound
        :rtype: bool
        """

        namespace = node.namespace

        if isinstance(namespace, ast.ClassDef) or is_dunder_name(name):
            return False

        if isinstance(namespace, ast.Module) and (self._exports is None or name in self._exports):
            return False

        binding = self.binding(node)
        if binding is None:
            return False

        return not any(reads_name(reference) for reference in binding.references)


class DeadCodeTransformer(SuiteTransformer):
    """
    Base class for transforms that remove statements that have no effect on a bound module

    The :attr:`changed` attribute is set if the last run removed anything.
    """

    def __call__(self, module):
        self.changed = False
        self.scope = ScopeAnalysis(module)
        return self.visit(module)

    def eliminate(self, node):
        """
        Remove a statement, or part of it

        :param node: The statement to consider
        :type node: ast.AST
        :return: The statement to keep, or None if it should be removed
        :rtype: ast.AST or None
        """

        return node

    def suite(self, node_list, parent):
        without_dead_code = []

        for node in node_list:
            node = self.eliminate(node)
            if node is not None:
                without_dead_code.append(self.visit(node))

        return self.non_empty(without_dead_code, parent)

    def non_empty(self, suite, parent):
        """
        Ensure a suite has a statement, if it needs one

        :param list suite: The statements in the suite
        :param parent: The node that owns the suite
        :type parent: ast.AST
        :rtype: list
        """

        if suite or isinstance(parent, ast.Module):
            return suite

        return [self.add_child(ast.Expr(value=ast.Num(0)), parent=parent)]
