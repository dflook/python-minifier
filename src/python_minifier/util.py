import ast

def is_ast_node(node, types):
    """
    Is a node one of the specified node types

    A node type may be an actual ast class, or a string naming one.
    types is a single node type or an iterable of many.

    If a node_type specified a specific Constant type (Str, Bytes, Num etc),
    returns true for Constant nodes of the correct type.

    :type node: ast.AST
    :param types:
    :rtype: bool

    """

    if not isinstance(types, tuple):
        types = (types,)

    actual_types = []
    for node_type in types:
        if isinstance(node_type, str):
            node_type = getattr(ast, node_type, None)
            if node_type is not None:
                actual_types.append(node_type)
        else:
            actual_types.append(node_type)

    if isinstance(node, tuple(actual_types)):
        return True

    if hasattr(ast, 'Constant') and isinstance(node, ast.Constant):
        if node.value in [None, True, False]:
            return ast.NameConstant in types
        elif isinstance(node.value, (int, float, complex)):
            return ast.Num in types
        elif isinstance(node.value, str):
            return ast.Str in types
        elif isinstance(node.value, bytes):
            return ast.Bytes in types
        elif node.value == Ellipsis:
            return ast.Ellipsis in types
        else:
            raise RuntimeError('Unknown Constant value %r' % type(node.value))

    return False

class NodeVisitor(object):
    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)

    def visit_Constant(self, node):
        if node.value in [None, True, False]:
            method = 'visit_NameConstant'
        elif isinstance(node.value, (int, float, complex)):
            method = 'visit_Num'
        elif isinstance(node.value, str):
            method = 'visit_Str'
        elif isinstance(node.value, bytes):
            method = 'visit_Bytes'
        elif node.value == Ellipsis:
            method = 'visit_Ellipsis'
        else:
            raise RuntimeError('Unknown Constant value %r' % type(node.value))

        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

