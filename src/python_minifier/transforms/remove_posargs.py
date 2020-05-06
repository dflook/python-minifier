import ast


def remove_posargs(node):
    if isinstance(node, ast.arguments):
        if hasattr(node, 'posonlyargs'):
            node.args = node.posonlyargs + node.args
            node.posonlyargs = []

    for child in ast.iter_child_nodes(node):
        remove_posargs(child)

    return node
