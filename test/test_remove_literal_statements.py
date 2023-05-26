import ast

import pytest

from python_minifier import add_namespace, bind_names, resolve_names, RemoveLiteralStatementsOptions
from python_minifier.ast_printer import print_ast
from python_minifier.transforms.remove_literal_statements import RemoveLiteralStatements
from python_minifier.ast_compare import compare_ast, CompareError

"""
Test cases:
    - Remove expression statements - module docstring, function docstring and class docstring are not removed; Test with all literal types, in module scope, function scope and class scope
    - Remove module docstring - function docstring, class docstring and expression statements are not removed; Test class and function docstrings in nested scope
    - Remove function docstring - module docstring, class docstring and expression statements are not removed; Test class and function docstrings in nested scope
    - Remove class docstring - module docstring, function docstring and expression statements are not removed; Test class and function docstrings in nested scope
    - Remove module docstring is suppressed by __doc__ builtin references; Test references in module scope, function scope and class scope
    - function and class docstrings are suppressed by __doc__ attribute references; Test references in module scope, function scope and class scope
"""


source = '''
"""Module docstring"""

"Module literal"
b"Module literal"
213
True
False
None
...
0.123
1.23e-4

def test():
    """Function docstring"""
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4

class Test:
    """Class docstring"""
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4    
    
    def test():
        """Function docstring"""
        "Module literal"
        b"Module literal"
        213
        True
        False
        None
        ...
        0.123
        1.23e-4
'''

def remove_literals(source, options):
    module = ast.parse(source, 'test_remove_literal_statements')

    add_namespace(module)
    bind_names(module)
    resolve_names(module)
    return RemoveLiteralStatements(options)(module)

def test_remove_literal_expression_statements():

    # Don't remove with remove_literal_expression_statements = False
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Do remove with defaults
    expected = '''
"""Module docstring"""

def test():
    """Function docstring"""

class Test:
    """Class docstring"""

    def test():
        """Function docstring"""
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions())

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Do remove with remove_literal_expression_statements = True
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_literal_expression_statements=True))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

def test_remove_module_docstring():

    # Don't remove with defaults
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Don't remove with remove_module_docstring=False
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_module_docstring=False, remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Do remove with remove_module_docstring=True
    expected = '''
"Module literal"
b"Module literal"
213
True
False
None
...
0.123
1.23e-4

def test():
    """Function docstring"""
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4

class Test:
    """Class docstring"""
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4    

    def test():
        """Function docstring"""
        "Module literal"
        b"Module literal"
        213
        True
        False
        None
        ...
        0.123
        1.23e-4
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_module_docstring=True, remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

def test_remove_function_docstring():

    # Dont' remove with defaults
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Don't remove is remove_function_docstrings=False
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_function_docstrings=False, remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Do remove if remove_function_docstrings=True
    expected = '''
"""Module docstring"""

"Module literal"
b"Module literal"
213
True
False
None
...
0.123
1.23e-4

def test():
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4

class Test:
    """Class docstring"""
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4    
    
    def test():
        "Module literal"
        b"Module literal"
        213
        True
        False
        None
        ...
        0.123
        1.23e-4
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_function_docstrings=True, remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise


def test_remove_class_docstring():

    # Dont' remove with defaults
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Don't remove is remove_function_docstrings=False
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_class_docstrings=False, remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # Do remove if remove_function_docstrings=True
    expected = '''
"""Module docstring"""

"Module literal"
b"Module literal"
213
True
False
None
...
0.123
1.23e-4

def test():
    """Function docstring"""
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4

class Test:
    "Module literal"
    b"Module literal"
    213
    True
    False
    None
    ...
    0.123
    1.23e-4    
    
    def test():
        """Function docstring"""
        "Module literal"
        b"Module literal"
        213
        True
        False
        None
        ...
        0.123
        1.23e-4
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_class_docstrings=True, remove_literal_expression_statements=False))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

def test_suppress_remove_module_docstring():

    source = '''
"""Module docstring"""

print(__doc__)

def test():
    """Function docstring"""

class Test:
    """Class docstring"""
    
    def test():
        """Function docstring"""
'''

    # function and class docstring still removed
    expected = '''
"""Module docstring"""

print(__doc__)

def test():0

class Test:
    def test():0
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_module_docstring=True, remove_function_docstrings=True, remove_class_docstrings=True))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise


    # With __doc__ in a nested scope

    source = '''
"""Module docstring"""

def test():
    """Function docstring"""

class Test:
    """Class docstring"""

    def test():
        """Function docstring"""
        
        def nested():
            print(__doc__)
'''

    # function and class docstring still removed
    expected = '''
"""Module docstring"""

def test():0

class Test:

    def test():
        
        def nested():
            print(__doc__)
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_module_docstring=True, remove_function_docstrings=True, remove_class_docstrings=True))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise


def test_suppress_remove_class_and_function_docstring():

    source = '''
"""Module docstring"""

def test():
    """Function docstring"""

class Test:
    """Class docstring"""

    def test():
        """Function docstring"""
        
print(test.__doc__)
'''

    # function and class docstring still removed
    expected = '''
def test():
    """Function docstring"""

class Test:
    """Class docstring"""

    def test():
        """Function docstring"""

print(test.__doc__)
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_module_docstring=True, remove_function_docstrings=True, remove_class_docstrings=True))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise

    # With __doc__ in a nested scope

    source = '''
"""Module docstring"""

def test():
    """Function docstring"""

class Test:
    """Class docstring"""

    def test():
        """Function docstring"""

        print(test.__doc__)
'''

    # function and class docstring still removed
    expected = '''
def test():
    """Function docstring"""

class Test:
    """Class docstring"""

    def test():
        """Function docstring"""

        print(test.__doc__)
'''

    expected_ast = ast.parse(expected)
    actual_ast = remove_literals(source, RemoveLiteralStatementsOptions(remove_module_docstring=True, remove_function_docstrings=True, remove_class_docstrings=True))

    try:
        compare_ast(expected_ast, actual_ast)
    except CompareError:
        print(print_ast(expected_ast))
        print(print_ast(actual_ast))
        raise
