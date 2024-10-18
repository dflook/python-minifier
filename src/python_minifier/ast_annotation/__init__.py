import ast

class NoParent(ast.AST):
    pass

def add_parent(node, parent=NoParent()):
    # type: (ast.AST, ast.AST) -> None
    node._parent = parent
    for child in ast.iter_child_nodes(node):
        add_parent(child, node)

def get_parent(node):
    # type: (ast.AST) -> ast.AST
    if isinstance(node, NoParent):
        raise ValueError('Node has no parent')
    return node._parent

def set_parent(node, parent):
    # type: (ast.AST, ast.AST) -> None
    node._parent = parent
