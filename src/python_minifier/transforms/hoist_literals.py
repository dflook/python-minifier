import ast
import sys

from python_minifier.transforms.name_generator import name_filter

class HoistLiterals(ast.NodeTransformer):
    """
    Hoist literal strings to module level variables
    """

    def __init__(self):

        self.mapping_namespace = True

        # key is namespace, value is a list of names referenced there
        self.names = set()

        # key is a namespace, value is a list of literals defined there
        self.string_literals = []
        self.bytes_literals = []

        # 'tainted' means an import * was found, so we have no idea what's in that namespace
        self.tainted = False

        self.hoisted_string = {}
        self.hoisted_bytes = {}

    def __call__(self, node):
        if sys.version_info < (2, 7):
            # collections.Counter doesn't exist for 2.6
            return node

        self.visit(node)

        if self.tainted:
            return node

        self.create_mapping()

        self.mapping_namespace = False
        node = self.visit(node)

        node.body = list(self.insert_mapping(node.body))
        return node

    def create_mapping(self):

        name_generator = name_filter(list(self.names))
        next_name = next(name_generator)

        from collections import Counter

        for string, count in Counter(self.string_literals).most_common():

            # The number of source characters used if we don't hoist this string:
            unhoisted_length = count * (len(string) + len('""'))

            # The number of source character used if we hoist this string
            hoisted_length = (count * len(next_name)) + len(next_name) + len('="') + len(string) + len('"')

            if hoisted_length < unhoisted_length:
                self.hoisted_string[string] = next_name
                next_name = next(name_generator)

        for bytes, count in Counter(self.bytes_literals).most_common():

            # The number of source used if we don't hoist this string:
            unhoisted_length = count * (len(bytes) + len('b""'))

            # The number of source character used if we hoist this string
            hoisted_length = (count * len(next_name)) + len(next_name) + len('=b"') + len(bytes) + len('"')

            if hoisted_length < unhoisted_length:
                self.hoisted_bytes[bytes] = next_name
                next_name = next(name_generator)

    def generate_mapping(self):
        for value, name in self.hoisted_string.items():
            yield ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store)], value=ast.Str(value))

        for value, name in self.hoisted_bytes.items():
            yield ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store)], value=ast.Bytes(value))

    def insert_mapping(self, node_list):

        inserted = False
        for node in node_list:

            if not inserted:
                if (isinstance(node, ast.ImportFrom) and node.module == '__future__') or (isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)):
                    pass
                else:
                    for n in self.generate_mapping():
                        yield n
                    inserted = True

            yield node

        if not inserted:
            for n in self.generate_mapping():
                yield n

    def visit_Module(self, node):
        node.body = [self.visit(n) for n in node.body]

        return node

    def visit_ClassDef(self, node):
        if self.mapping_namespace:
            self._add_to_namespace(node.name)

        node.body = list(self.insert_mapping(node.body))

        return node

    def visit_alias(self, node):
        if self.mapping_namespace:
            if node.asname:
                self._add_to_namespace(node.asname)
            else:
                self._add_to_namespace(node.name)

                if node.name == '*':
                    # We can't know everything in our namespace if there is an import *
                    # So we can't safely create new variables
                    self._taint()

        return node

    def visit_FunctionDef(self, node):
        if self.mapping_namespace:
            self._add_to_namespace(node.name)

        if node.args:
            node.args = self.visit(node.args)

        node.body = [self.visit(n) for n in node.body]

        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_arguments(self, node):

        if node.args:
            node.args = [self.visit(a) for a in node.args]

        if hasattr(node, 'kwonlyargs') and node.kwonlyargs:
            node.kwonlyargs = [self.visit(a) for a in node.kwonlyargs]

        if self.mapping_namespace:

            if hasattr(node, 'varargannotation') or sys.version_info < (3,0):
                # Python < 3.4, vararg and kwarg are raw strings

                if node.vararg:
                    self._add_to_namespace(node.vararg)
                if node.kwarg:
                    self._add_to_namespace(node.kwarg)

            else:
                # Python > 3.4, vararg and kwarg are arg nodes

                if node.vararg:
                    node.vararg = self.visit(node.vararg)

                if node.kwarg:
                    node.kwarg = self.visit(node.kwarg)

        return node

    def visit_arg(self, node):
        if isinstance(node, ast.Name):
            # Python 2 uses Name nodes
            return self.visit_Name(node)

        if self.mapping_namespace:
            self._add_to_namespace(node.arg)
        return node

    def visit_Name(self, node):
        if self.mapping_namespace:
            self._add_to_namespace(node.id)
        return node

    def visit_Global(self, node):
        if self.mapping_namespace:
            [self._add_to_namespace(name) for name in node.names]
        return node

    def visit_Nonlocal(self, node):
        if self.mapping_namespace:
            [self._add_to_namespace(name) for name in node.names]
        return node

    def _add_to_namespace(self, name):
        self.names.add(name)

    def _taint(self):
        self.tainted = True

    def visit_Str(self, node):
        if self.mapping_namespace:
            self.string_literals.append(node.s)
        else:
            if node.s in self.hoisted_string:
                return ast.Name(id=self.hoisted_string[node.s], ctx=ast.Load)

        return node

    def visit_Bytes(self, node):
        if self.mapping_namespace:
            self.bytes_literals.append(node.s)
        else:
            if node.s in self.hoisted_bytes:
                return ast.Name(id=self.hoisted_bytes[node.s], ctx=ast.Load)

        return node

    def visit_JoinedStr(self, node):
        for v in node.values:
            if isinstance(v, ast.Str):
                # Can't hoist this!
                continue
            else:
                self.visit(v)

        return node