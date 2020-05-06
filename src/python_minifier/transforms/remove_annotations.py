import ast
import sys

from python_minifier.transforms.suite_transformer import SuiteTransformer


class RemoveAnnotations(SuiteTransformer):
    """
    Remove type annotations from source
    """

    def __call__(self, node):
        if sys.version_info < (3, 0):
            return node
        return self.visit(node)

    def visit_FunctionDef(self, node):
        node.args = self.visit_arguments(node.args)
        node.body = self.suite(node.body, parent=node)
        node.decorator_list = [self.visit(d) for d in node.decorator_list]

        if hasattr(node, 'returns'):
            node.returns = None

        return node

    def visit_arguments(self, node):
        assert isinstance(node, ast.arguments)

        if hasattr(node, 'posonlyargs') and node.posonlyargs:
            node.posonlyargs = [self.visit_arg(a) for a in node.posonlyargs]

        if node.args:
            node.args = [self.visit_arg(a) for a in node.args]

        if hasattr(node, 'kwonlyargs') and node.kwonlyargs:
            node.kwonlyargs = [self.visit_arg(a) for a in node.kwonlyargs]

        if hasattr(node, 'varargannotation'):
            node.varargannotation = None
        else:
            if node.vararg:
                node.vararg = self.visit_arg(node.vararg)

        if hasattr(node, 'kwargannotation'):
            node.kwargannotation = None
        else:
            if node.kwarg:
                node.kwarg = self.visit_arg(node.kwarg)

        return node

    def visit_arg(self, node):
        node.annotation = None
        return node

    def visit_AnnAssign(self, node):
        def is_dataclass_field(node):
            if sys.version_info < (3, 7):
                return False

            if not isinstance(node.parent, ast.ClassDef):
                return False

            if len(node.parent.decorator_list) == 0:
                return False

            for node in node.parent.decorator_list:
                if isinstance(node, ast.Name) and node.id == 'dataclass':
                    return True
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'dataclass':
                    return True

            return False

        if is_dataclass_field(node):
            return node
        elif node.value:
            return self.add_child(ast.Assign([node.target], node.value), parent=node.parent)
        else:
            # Valueless annotations cause the interpreter to treat the variable as a local.
            # I don't know of another way to do that without assigning to it, so
            # keep it as an AnnAssign, but replace the annotation with '0'

            node.annotation = self.add_child(ast.Num(0), parent=node.parent)
            return node
