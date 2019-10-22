"""
For each node in an AST set the namespace to use for name binding and resolution
"""

import ast

from python_minifier.rename.util import is_namespace


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

        if isinstance(node, ast.FunctionDef) or (
            hasattr(ast, 'AsyncFunctionDef') and isinstance(node, ast.AsyncFunctionDef)
        ):
            add_parent_to_functiondef(node)
        elif isinstance(node, ast.Lambda):
            add_parent_to_arguments(node.args, func=node)
            add_parent(node.body, parent=node, namespace=node)
        elif isinstance(node, ast.ClassDef):
            add_parent_to_classdef(node)
        else:
            for child in ast.iter_child_nodes(node):
                add_parent(child, parent=node, namespace=node)

        return

    if isinstance(node, ast.comprehension):
        add_parent(node.target, parent=node, namespace=namespace)
        add_parent(node.iter, parent=node, namespace=namespace)
        for if_ in node.ifs:
            add_parent(if_, parent=node, namespace=namespace)
        return

    if isinstance(node, ast.Global):
        namespace.global_names.update(node.names)
    if hasattr(ast, 'Nonlocal') and isinstance(node, ast.Nonlocal):
        namespace.nonlocal_names.update(node.names)

    for child in ast.iter_child_nodes(node):
        add_parent(child, parent=node, namespace=namespace)


def add_namespace(module):
    add_parent(module)
