import python_minifier.ast_compat as ast
from python_minifier.ast_annotation import add_parent

from python_minifier.rename import add_namespace, resolve_names
from python_minifier.rename.bind_names import bind_names
from python_minifier.rename.util import iter_child_namespaces
from python_minifier.util import is_constant_node


def assert_namespace_tree(source, expected_tree):
    tree = ast.parse(source)

    add_parent(tree)
    add_namespace(tree)
    bind_names(tree)
    resolve_names(tree)

    actual = print_namespace(tree)

    print(actual)
    assert actual.strip() == expected_tree.strip()


def print_namespace(namespace, indent=''):
    s = ''

    if not indent:
        s += '\n'

    def namespace_name(node):
        if is_constant_node(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return 'Function ' + node.name
        elif isinstance(node, ast.ClassDef):
            return 'Class ' + node.name
        else:
            return namespace.__class__.__name__

    s += indent + '+ ' + namespace_name(namespace) + '\n'

    for name in sorted(namespace.global_names):
        s += indent + '  - global ' + name + '\n'

    for name in sorted(namespace.nonlocal_names):
        s += indent + '  - nonlocal ' + name + '\n'

    for binding in sorted(namespace.bindings, key=lambda b: b.name or str(b.value)):
        s += indent + '  - ' + repr(binding) + '\n'

    for child in iter_child_namespaces(namespace):
        s += print_namespace(child, indent=indent + '  ')

    return s
