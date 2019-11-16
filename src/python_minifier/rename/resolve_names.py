import ast

from python_minifier.rename.binding import BuiltinBinding, NameBinding
from python_minifier.rename.util import get_global_namespace, get_nonlocal_namespace, builtins


def get_binding(name, namespace):
    if name in namespace.global_names and not isinstance(namespace, ast.Module):
        return get_binding(name, get_global_namespace(namespace))
    elif name in namespace.nonlocal_names and not isinstance(namespace, ast.Module):
        return get_binding(name, get_nonlocal_namespace(namespace))

    for binding in namespace.bindings:
        if binding.name == name:
            return binding

    if not isinstance(namespace, ast.Module):
        return get_binding(name, get_nonlocal_namespace(namespace))

    else:
        # This is unresolved at global scope - is it a builtin?
        if name in dir(builtins):
            if name in ['exec', 'eval', 'locals', 'globals', 'vars']:
                namespace.tainted = True

            binding = BuiltinBinding(name, namespace, rename_cost=len(name) + 1)
            namespace.bindings.append(binding)
            return binding

        else:
            binding = NameBinding(name)
            binding.disallow_rename()
            namespace.bindings.append(binding)
            return binding


def resolve_names(node):
    """
    Resolve unbound names to a NameBinding

    :param node: The module to resolve names in
    :type node: :class:`ast.Module`

    """

    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        get_binding(node.id, node.namespace).add_reference(node)
    elif hasattr(ast, 'Exec') and isinstance(node, ast.Exec):
        get_global_namespace(node).tainted = True

    for child in ast.iter_child_nodes(node):
        resolve_names(child)
