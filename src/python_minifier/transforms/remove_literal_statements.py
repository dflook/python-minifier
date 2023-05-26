import ast

from python_minifier.transforms.remove_literal_statements_options import RemoveLiteralStatementsOptions
from python_minifier.transforms.suite_transformer import SuiteTransformer
from python_minifier.util import is_ast_node

class RemoveLiteralStatements(SuiteTransformer):
    """
    Remove literal expressions from the code

    This includes docstrings
    """

    def __init__(self, options):
        assert isinstance(options, RemoveLiteralStatementsOptions)
        self._options = options
        super(RemoveLiteralStatements, self).__init__()

    def __call__(self, node):
        assert isinstance(node, ast.Module)

        def has_doc_attribute(node):
            if isinstance(node, ast.Attribute):
                if node.attr == '__doc__':
                    return True

            for child in ast.iter_child_nodes(node):
                if has_doc_attribute(child):
                    return True

            return False

        def has_doc_binding(node):
            for binding in node.bindings:
                if binding.name == '__doc__':
                    return True
            return False

        self._has_doc_attribute = has_doc_attribute(node)
        self._has_doc_binding = has_doc_binding(node)
        return self.visit(node)

    def without_literal_statements(self, node_list):
        """
        Remove all literal statements except for docstrings
        """

        def is_docstring(node):
            assert isinstance(node, ast.Expr)

            if not is_ast_node(node.value, ast.Str):
                return False

            if is_ast_node(node.parent, (ast.FunctionDef, 'AsyncFunctionDef', ast.ClassDef, ast.Module)):
                return node.parent.body[0] is node

            return False

        def is_literal_statement(node):
            if not isinstance(node, ast.Expr):
                return False

            if is_docstring(node):
                return False

            return is_ast_node(node.value, (ast.Num, ast.Str, 'NameConstant', 'Bytes', ast.Ellipsis))

        return [n for n in node_list if not is_literal_statement(n)]

    def without_docstring(self, node_list):
        if node_list == []:
            return node_list

        if not isinstance(node_list[0], ast.Expr):
            return node_list

        if isinstance(node_list[0].value, ast.Str):
            return node_list[1:]

        return node_list

    def suite(self, node_list, parent):
        suite = [self.visit(node) for node in node_list]

        if self._options.remove_literal_expression_statements is True:
            suite = self.without_literal_statements(node_list)

        if isinstance(parent, ast.Module) and self._options.remove_module_docstring is True and self._has_doc_binding is False:
            suite = self.without_docstring(node_list)
        elif is_ast_node(parent, (ast.FunctionDef, 'AsyncFunctionDef')) and self._options.remove_function_docstrings is True and self._has_doc_attribute is False:
            suite = self.without_docstring(node_list)
        elif is_ast_node(parent, ast.ClassDef) and self._options.remove_class_docstrings is True and self._has_doc_attribute is False:
            suite = self.without_docstring(node_list)

        if len(suite) == 0:
            if isinstance(parent, ast.Module):
                return []
            else:
                return [self.add_child(ast.Expr(value=ast.Num(0)), parent=parent)]

        return suite
