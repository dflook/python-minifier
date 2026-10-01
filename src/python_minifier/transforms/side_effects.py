import python_minifier.ast_compat as ast
from python_minifier.util import is_constant_node

_FSTRINGS = tuple(getattr(ast, name) for name in ('JoinedStr', 'FormattedValue') if hasattr(ast, name))


def is_side_effect_free(node):
    """
    Is evaluating an expression, and discarding the result, known to do nothing?

    The analysis is conservative, anything that is not known to be harmless is assumed to
    have side effects. Calls, ``await``, ``yield``, assignment expressions and
    comprehensions are never side effect free. Looking up a name, accessing an
    attribute or subscript and applying an operator are assumed not to run code that
    matters, and so are not considered to have side effects.

    :param node: The expression to check, or None
    :type node: ast.AST or None
    :rtype: bool
    """

    if node is None:
        return True

    if is_constant_node(node, (ast.Num, ast.Str, ast.Bytes, ast.NameConstant, ast.Ellipsis)) or isinstance(node, ast.Name):
        return True

    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(is_side_effect_free(element) for element in node.elts)

    if isinstance(node, ast.Dict):
        return all(key is not None and is_side_effect_free(key) for key in node.keys) and all(is_side_effect_free(value) for value in node.values)

    if isinstance(node, ast.UnaryOp):
        return is_side_effect_free(node.operand)

    if isinstance(node, ast.BinOp):
        return is_side_effect_free(node.left) and is_side_effect_free(node.right)

    if isinstance(node, ast.BoolOp):
        return all(is_side_effect_free(value) for value in node.values)

    if isinstance(node, ast.Compare):
        return is_side_effect_free(node.left) and all(is_side_effect_free(comparator) for comparator in node.comparators)

    if isinstance(node, ast.IfExp):
        return is_side_effect_free(node.test) and is_side_effect_free(node.body) and is_side_effect_free(node.orelse)

    if isinstance(node, ast.Attribute):
        return is_side_effect_free(node.value)

    if isinstance(node, ast.Subscript):
        return is_side_effect_free(node.value) and is_side_effect_free(node.slice)

    if isinstance(node, ast.Slice):
        return is_side_effect_free(node.lower) and is_side_effect_free(node.upper) and is_side_effect_free(node.step)

    if isinstance(node, ast.Index):
        return is_side_effect_free(node.value)

    if isinstance(node, ast.ExtSlice):
        return all(is_side_effect_free(dim) for dim in node.dims)

    if isinstance(node, ast.Lambda):
        return _are_defaults_side_effect_free(node.args)

    if isinstance(node, _FSTRINGS):
        if hasattr(node, 'values'):
            return all(is_side_effect_free(value) for value in node.values)
        return is_side_effect_free(node.value) and is_side_effect_free(node.format_spec)

    return False


def _are_defaults_side_effect_free(arguments):
    defaults = list(arguments.defaults) + list(getattr(arguments, 'kw_defaults', []))
    return all(is_side_effect_free(default) for default in defaults)


def is_definition_side_effect_free(node):
    """
    Is executing a function or class definition, and discarding the result, known to do nothing?

    Defining a function evaluates its default values and annotations. Defining a class evaluates its
    bases and keywords and runs its body.
    Decorators are not considered, a decorated definition is never side effect free.

    :param node: The definition to check
    :type node: ast.FunctionDef or ast.AsyncFunctionDef or ast.ClassDef
    :rtype: bool
    """

    if node.decorator_list:
        return False

    if isinstance(node, ast.ClassDef):
        expressions = list(node.bases) + [keyword.value for keyword in getattr(node, 'keywords', [])]
        expressions += [getattr(node, name) for name in ('starargs', 'kwargs') if getattr(node, name, None) is not None]
        return all(is_side_effect_free(expression) for expression in expressions) and all(_is_class_statement_side_effect_free(statement) for statement in node.body)

    arguments = node.args
    annotations = [getattr(node, 'returns', None)]
    annotations += [getattr(arg, 'annotation', None) for arg in getattr(arguments, 'posonlyargs', []) + arguments.args + getattr(arguments, 'kwonlyargs', [])]
    annotations += [getattr(arguments, name, None) for name in ('varargannotation', 'kwargannotation')]
    if isinstance(arguments.vararg, ast.arg):
        annotations.append(arguments.vararg.annotation)
    if isinstance(arguments.kwarg, ast.arg):
        annotations.append(arguments.kwarg.annotation)

    return _are_defaults_side_effect_free(arguments) and all(is_side_effect_free(annotation) for annotation in annotations)


def _is_class_statement_side_effect_free(statement):
    if isinstance(statement, ast.Pass):
        return True

    if isinstance(statement, ast.Expr):
        return is_side_effect_free(statement.value)

    if isinstance(statement, ast.Assign):
        return is_side_effect_free(statement.value) and all(isinstance(target, ast.Name) for target in statement.targets)

    if isinstance(statement, ast.AnnAssign):
        return isinstance(statement.target, ast.Name) and is_side_effect_free(statement.annotation) and is_side_effect_free(statement.value)

    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return is_definition_side_effect_free(statement)

    return False
