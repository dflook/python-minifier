import ast

from python_minifier.util import is_ast_node


def implicit_return_none(node):

    if isinstance(node, ast.Return) and is_ast_node(node.value, 'NameConstant') and node.value.value is None:
        # explicit return None
        node.value = None

    for child in ast.iter_child_nodes(node):
        implicit_return_none(child)

    return node
