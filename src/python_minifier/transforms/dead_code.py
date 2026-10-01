from python_minifier.rename import add_namespace, bind_names, resolve_names
from python_minifier.transforms.remove_unreachable import RemoveUnreachable
from python_minifier.transforms.remove_unused_definitions import RemoveUnusedDefinitions
from python_minifier.transforms.remove_unused_imports import RemoveUnusedImports
from python_minifier.transforms.remove_unused_variables import RemoveUnusedVariables


def eliminate_dead_code(module, remove_imports, remove_variables, remove_definitions, remove_unreachable):
    """
    Remove code that has no effect from a module

    Removing code can make more code dead, for example removing an unused function can leave the names
    it used unused. This repeats until there is nothing left to remove.

    Modules that are tainted, because they use features like star imports or ``exec``, are not changed.

    The names in the module are left unbound on return.

    :param module: The module to remove dead code from
    :type module: ast.Module
    :param bool remove_imports: If unused imports should be removed
    :param bool remove_variables: If assignments to unused variables should be removed
    :param bool remove_definitions: If unused function and class definitions should be removed
    :param bool remove_unreachable: If statements after return, raise, break or continue should be removed
    :rtype: ast.Module
    """

    transforms = []
    if remove_unreachable:
        transforms.append(RemoveUnreachable())
    if remove_definitions:
        transforms.append(RemoveUnusedDefinitions())
    if remove_variables:
        transforms.append(RemoveUnusedVariables())
    if remove_imports:
        transforms.append(RemoveUnusedImports())

    changed = True
    while changed:
        # Names must be bound again to account for what was removed in the last pass
        add_namespace(module)
        bind_names(module)
        resolve_names(module)

        if module.tainted:
            break

        changed = False
        for transform in transforms:
            module = transform(module)
            changed = changed or transform.changed

    add_namespace(module)
    return module
