import ast

from python_minifier.rename.binding import BuiltinBinding, NameBinding
from python_minifier.rename.util import get_global_namespace, get_nonlocal_namespace, builtins
from python_minifier.util import is_ast_node


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

            binding = BuiltinBinding(name, namespace)
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
    elif isinstance(node, ast.Name) and node.id in node.namespace.nonlocal_names:
        get_binding(node.id, node.namespace).add_reference(node)

    elif isinstance(node, ast.ClassDef) and node.name in node.namespace.nonlocal_names:
        get_binding(node.name, node.namespace).add_reference(node)
    elif is_ast_node(node, (ast.FunctionDef, 'AsyncFunctionDef')) and node.name in node.namespace.nonlocal_names:
        get_binding(node.name, node.namespace).add_reference(node)
    elif isinstance(node, ast.alias):

        if node.asname is not None:
            if node.asname in node.namespace.nonlocal_names:
                get_binding(node.asname, node.namespace).add_reference(node)
        else:
            # This binds the root module only for a dotted import
            root_module = node.name.split('.')[0]

            if root_module in node.namespace.nonlocal_names:
                binding = get_binding(root_module, node.namespace)
                binding.add_reference(node)

                if '.' in node.name:
                    binding.disallow_rename()

    elif isinstance(node, ast.ExceptHandler) and node.name is not None:
        if isinstance(node.name, str) and node.name in node.namespace.nonlocal_names:
            get_binding(node.name, node.namespace).add_reference(node)

    elif is_ast_node(node, 'Nonlocal'):
        for name in node.names:
            get_binding(name, node.namespace).add_reference(node)
    elif is_ast_node(node, ('MatchAs', 'MatchStar')) and node.name in node.namespace.nonlocal_names:
        get_binding(node.name, node.namespace).add_reference(node)
    elif is_ast_node(node, 'MatchMapping') and node.rest in node.namespace.nonlocal_names:
        get_binding(node.rest, node.namespace).add_reference(node)

    elif is_ast_node(node, 'Exec'):
        get_global_namespace(node).tainted = True

    for child in ast.iter_child_nodes(node):
        resolve_names(child)
