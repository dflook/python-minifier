"""
For each node in an AST set the namespace to use for name binding and resolution
"""

import python_minifier.ast_compat as ast

from python_minifier.rename.util import is_namespace
from python_minifier.util import is_ast_node


def add_parent_to_arguments(arguments, func):
    arguments.parent = func
    arguments.namespace = func

    for arg in getattr(arguments, 'posonlyargs', []) + arguments.args:
        add_parent(arg, arguments, func)
        if hasattr(arg, 'annotation') and arg.annotation is not None:
            add_parent(arg.annotation, arguments, func.namespace)

    if hasattr(arguments, 'kwonlyargs'):
        for arg in arguments.kwonlyargs:
            add_parent(arg, arguments, func)
            if arg.annotation is not None:
                add_parent(arg.annotation, arguments, func.namespace)

        for node in arguments.kw_defaults:
            if node is not None:
                add_parent(node, arguments, func.namespace)

    for node in arguments.defaults:
        add_parent(node, arguments, func.namespace)

    if arguments.vararg:
        if hasattr(arguments, 'varargannotation') and arguments.varargannotation is not None:
            add_parent(arguments.varargannotation, arguments, func.namespace)
        elif isinstance(arguments.vararg, str):
            pass
        else:
            add_parent(arguments.vararg, arguments, func)

    if arguments.kwarg:
        if hasattr(arguments, 'kwargannotation') and arguments.kwargannotation is not None:
            add_parent(arguments.kwargannotation, arguments, func.namespace)
        elif isinstance(arguments.kwarg, str):
            pass
        else:
            add_parent(arguments.kwarg, arguments, func)


def add_parent_to_functiondef(functiondef):
    """
    Add correct parent and namespace attributes to functiondef nodes
    """

    if functiondef.args is not None:
        add_parent_to_arguments(functiondef.args, func=functiondef)

    for node in functiondef.body:
        add_parent(node, parent=functiondef, namespace=functiondef)

    for node in functiondef.decorator_list:
        add_parent(node, parent=functiondef, namespace=functiondef.namespace)

    if hasattr(functiondef, 'type_params') and functiondef.type_params is not None:
        for node in functiondef.type_params:
            add_parent(node, parent=functiondef, namespace=functiondef.namespace)

    if hasattr(functiondef, 'returns') and functiondef.returns is not None:
        add_parent(functiondef.returns, parent=functiondef, namespace=functiondef.namespace)


def add_parent_to_classdef(classdef):
    """
    Add correct parent and namespace attributes to classdef nodes
    """

    for node in classdef.bases:
        add_parent(node, parent=classdef, namespace=classdef.namespace)

    if hasattr(classdef, 'keywords'):
        for node in classdef.keywords:
            add_parent(node, parent=classdef, namespace=classdef.namespace)

    if hasattr(classdef, 'starargs') and classdef.starargs is not None:
        add_parent(classdef.starargs, parent=classdef, namespace=classdef.namespace)

    if hasattr(classdef, 'kwargs') and classdef.kwargs is not None:
        add_parent(classdef.kwargs, parent=classdef, namespace=classdef.namespace)

    for node in classdef.body:
        add_parent(node, parent=classdef, namespace=classdef)

    for node in classdef.decorator_list:
        add_parent(node, parent=classdef, namespace=classdef.namespace)

    if hasattr(classdef, 'type_params') and classdef.type_params is not None:
        for node in classdef.type_params:
            add_parent(node, parent=classdef, namespace=classdef.namespace)

def add_parent_to_comprehension(node, namespace):
    assert is_ast_node(node, (ast.GeneratorExp, 'SetComp', 'DictComp', 'ListComp'))

    if hasattr(node, 'elt'):
        add_parent(node.elt, parent=node, namespace=node)
    elif hasattr(node, 'key'):
        add_parent(node.key, parent=node, namespace=node)
        add_parent(node.value, parent=node, namespace=node)

    iter_namespace = namespace
    for generator in node.generators:
        generator.parent = node
        generator.namespace = node

        add_parent(generator.target, parent=generator, namespace=node)
        add_parent(generator.iter, parent=generator, namespace=iter_namespace)
        iter_namespace = node
        for if_ in generator.ifs:
            add_parent(if_, parent=generator, namespace=node)


def add_parent(node, parent=None, namespace=None):
    """
    Add a parent attribute to child nodes
    Add a namespace attribute to child nodes

    :param node: The tree to add parent and namespace properties to
    :type node: :class:`ast.AST`
    :param parent: The parent node of this node
    :type parent: :class:`ast.AST`
    :param namespace: The namespace Node that this node is in
    :type namespace: ast.Lambda or ast.Module or ast.FunctionDef or ast.AsyncFunctionDef or ast.ClassDef or ast.DictComp or ast.SetComp or ast.ListComp or ast.Generator

    """

    node.parent = parent if parent is not None else node
    node.namespace = namespace if namespace is not None else node

    if is_namespace(node):
        node.bindings = []
        node.global_names = set()
        node.nonlocal_names = set()

        if is_ast_node(node, (ast.FunctionDef, 'AsyncFunctionDef')):
            add_parent_to_functiondef(node)
        elif is_ast_node(node, (ast.GeneratorExp, 'SetComp', 'DictComp', 'ListComp')):
            add_parent_to_comprehension(node, namespace=namespace)
        elif isinstance(node, ast.Lambda):
            add_parent_to_arguments(node.args, func=node)
            add_parent(node.body, parent=node, namespace=node)
        elif isinstance(node, ast.ClassDef):
            add_parent_to_classdef(node)
        else:
            for child in ast.iter_child_nodes(node):
                add_parent(child, parent=node, namespace=node)

        return

    if isinstance(node, ast.Global):
        namespace.global_names.update(node.names)
    if is_ast_node(node, 'Nonlocal'):
        namespace.nonlocal_names.update(node.names)

    if isinstance(node, ast.Name):
        if isinstance(namespace, ast.ClassDef):
            if isinstance(node.ctx, ast.Load):
                namespace.nonlocal_names.add(node.id)
            elif isinstance(node.ctx, ast.Store) and isinstance(node.parent, ast.AugAssign):
                namespace.nonlocal_names.add(node.id)

    for child in ast.iter_child_nodes(node):
        add_parent(child, parent=node, namespace=namespace)


def add_namespace(module):
    add_parent(module)
