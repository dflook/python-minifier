import ast
import sys

from python_minifier.util import is_ast_node


def implicit_return_none(node):

    if isinstance(node, ast.Return):
        if sys.version_info < (3, 4) and is_ast_node(node.value, 'Name') and node.value.id == 'None':
            # explicit return None
            node.value = None

        elif sys.version_info >= (3, 4) and is_ast_node(node.value, 'NameConstant') and node.value.value is None:
            # explicit return None
            node.value = None

    for child in ast.iter_child_nodes(node):
        implicit_return_none(child)

    return node
