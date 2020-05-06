import ast

from python_minifier.rename.binding import NameBinding
from python_minifier.rename.util import arg_rename_in_place, get_global_namespace, get_nonlocal_namespace, builtins
from python_minifier.transforms.suite_transformer import NodeVisitor


class NameBinder(NodeVisitor):
    """
    Create a NameBinding for each name that is bound

    The NameBinding is added to the bindings dictionary in the namespace node the name is local to.
    """

    def __call__(self, module):
        assert isinstance(module, ast.Module)
        module.tainted = False
        return self.visit(module)

    def get_binding(self, name, namespace):
        if name in namespace.global_names and not isinstance(namespace, ast.Module):
            return self.get_binding(name, get_global_namespace(namespace))
        elif name in namespace.nonlocal_names and not isinstance(namespace, ast.Module):
            return self.get_binding(name, get_nonlocal_namespace(namespace))

        if isinstance(namespace, ast.ClassDef):
            binding = self.get_binding(name, get_nonlocal_namespace(namespace))
            binding.disallow_rename()
            return binding

        for binding in namespace.bindings:
            if binding.name == name:
                break
        else:  # weeee!
            binding = NameBinding(name)
            namespace.bindings.append(binding)

            if name in dir(builtins):
                binding.disallow_rename()

        if name in namespace.nonlocal_names and isinstance(namespace, ast.Module):
            # This is actually a syntax error - but we want the same syntax error after minifying!
            binding.disallow_rename()

        return binding

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store) or isinstance(node.ctx, ast.Del):
            self.get_binding(node.id, node.namespace).add_reference(node)

        if isinstance(node.ctx, ast.Param):
            binding = self.get_binding(node.id, node.namespace)

            if arg_rename_in_place(node):
                binding.add_reference(node)
            else:
                binding.add_reference(
                    node, reserved=node.id, rename_cost=(len(node.id) * 2) + 2
                )  # Assuming that the new name is only a single character

                if isinstance(node.namespace, ast.Lambda):
                    # Lambda function arguments can't be renamed without breaking keyword arguments
                    binding.disallow_rename()

    def visit_ClassDef(self, node):
        self.get_binding(node.name, node.namespace).add_reference(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.get_binding(node.name, node.namespace).add_reference(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_alias(self, node):
        if node.name == '*':
            get_global_namespace(node).tainted = True

        root_module = node.name.split('.')[0]

        if root_module == 'timeit':
            get_global_namespace(node).tainted = True

        if node.asname is not None:
            self.get_binding(node.asname, node.namespace).add_reference(node)
        else:
            # This binds the root module only for a dotted import

            binding = self.get_binding(root_module, node.namespace)
            binding.add_reference(node, rename_cost=len(node.name) + 4)

            if '.' in node.name:
                binding.disallow_rename()

    def visit_arguments(self, node):
        if isinstance(node.vararg, str):
            binding = self.get_binding(node.vararg, node.namespace)
            binding.add_reference(node)

        if isinstance(node.kwarg, str):
            binding = self.get_binding(node.kwarg, node.namespace)
            binding.add_reference(node)

        self.generic_visit(node)

    def visit_arg(self, node):
        binding = self.get_binding(node.arg, node.namespace)

        if arg_rename_in_place(node):
            binding.add_reference(node)
        else:
            binding.add_reference(
                node, reserved=node.arg, rename_cost=(len(node.arg) * 2) + 2
            )  # Assuming that the new name is only a single character

            if isinstance(node.namespace, ast.Lambda):
                # Lambda function arguments can't be renamed without breaking keyword arguments
                binding.disallow_rename()

        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.name is not None:
            if isinstance(node.name, str):
                # python 3
                self.get_binding(node.name, node.namespace).add_reference(node)
            else:
                # In python 2 the name is a Name node,
                # which will be visited by generic_visit
                pass

        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            self.get_binding(name, node.namespace).add_reference(node)

    def visit_Nonlocal(self, node):
        for name in node.names:
            self.get_binding(name, node.namespace).add_reference(node)


def bind_names(module):
    """
    Bind names to their local namespace

    :param module: The module to bind names in
    :type: :class:`ast.Module`

    """

    NameBinder()(module)
