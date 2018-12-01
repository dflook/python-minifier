import ast

from python_minifier.rename.binding import Binding
from python_minifier.rename.util import insert


class Replacer(ast.NodeTransformer):
    def __init__(self, replace, name):
        self.replace = replace
        self.name = name

    def visit_NameConstant(self, node):
        if node in self.replace:
            return ast.Name(id=self.name, ctx=ast.Load())
        return node

    def visit_Str(self, node):
        if node in self.replace:
            return ast.Name(id=self.name, ctx=ast.Load())
        return node

    def visit_Bytes(self, node):
        return self.visit_Str(node)

    def visit_JoinedStr(self, node):
        node.values = [self.visit(v) if isinstance(v, ast.Str) else v for v in node.values]
        return node


class HoistedLiteral(Binding):
    def __init__(self, value, namespace, *args, **kwargs):
        super(HoistedLiteral, self).__init__(*args, **kwargs)
        self._value = value
        self.namespace = namespace

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return self.__class__.__name__ + '(value=%r)' % self._value.s

    def rename(self, new_name):
        Replacer(self.references, new_name).visit(self.namespace)

        self.namespace.body = list(
            insert(self.namespace.body, ast.Assign(targets=[ast.Name(id=new_name, ctx=ast.Store())], value=self._value))
        )

        self._name = new_name

    def should_rename(self, new_name):
        current_cost = len(self.references) * len(repr(self._value.s))
        rename_cost = (len(self.references) * len(new_name)) + self._rename_cost

        return rename_cost <= current_cost


class HoistedConstant(HoistedLiteral):
    def __repr__(self):
        return self.__class__.__name__ + '(value=%r)' % self._value.value

    def should_rename(self, new_name):
        current_cost = len(self.references) * len(repr(self._value.value))
        rename_cost = (len(self.references) * len(new_name)) + self._rename_cost

        return rename_cost <= current_cost


class HoistLiterals(ast.NodeVisitor):
    """
    Hoist literal strings to module level variables
    """

    def __call__(self, module):
        self.module = module
        self.visit(module)

    def visit_Str(self, node):

        if isinstance(node.parent, ast.Expr):
            # This is literal statement
            # The RemoveLiteralStatements transformer must have left it here, so ignore it.
            return

        def get_binding():
            for binding in self.module.bindings:
                if type(binding) is HoistedLiteral:
                    if type(binding.value.s) == type(node.s) and binding.value.s == node.s:
                        return binding
            binding = HoistedLiteral(node, self.module, rename_cost=len('=' + repr(node.s)))
            self.module.bindings.append(binding)
            return binding

        get_binding().add_reference(node)

    def visit_Bytes(self, node):
        self.visit_Str(node)

    def visit_JoinedStr(self, node):
        for v in node.values:
            if isinstance(v, ast.Str):
                # Can't hoist this!
                continue
            else:
                self.visit(v)

    def visit_NameConstant(self, node):
        def get_binding():
            for binding in self.module.bindings:
                if type(binding) is HoistedConstant and binding.value.value == node.value:
                    return binding
            binding = HoistedConstant(node, self.module, rename_cost=len('=' + repr(node.value)))
            self.module.bindings.append(binding)
            return binding

        get_binding().add_reference(node)


def rename_literals(module):
    HoistLiterals()(module)
