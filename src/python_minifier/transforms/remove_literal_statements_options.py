class RemoveLiteralStatementsOptions(object):
    """
    Options for the RemoveLiteralStatements transform

    This can be passed to the minify function as the remove_literal_statements argument

    :param remove_module_docstring: Remove module docstring
    :type remove_module_docstring: bool
    :param remove_function_docstrings: Remove function docstrings
    :type remove_function_docstrings: bool
    :param remove_class_docstrings: Remove class docstrings
    :type remove_class_docstrings: bool
    :param remove_literal_expression_statements: Remove non-docstring literal statements
    :type remove_literal_expression_statements: bool
    """

    remove_module_docstring = False
    remove_function_docstrings = False
    remove_class_docstrings = False
    remove_literal_expression_statements = True

    def __init__(self, remove_module_docstring=False, remove_function_docstrings=False, remove_class_docstrings=False, remove_literal_expression_statements=True):
        self.remove_module_docstring = remove_module_docstring
        self.remove_function_docstrings = remove_function_docstrings
        self.remove_class_docstrings = remove_class_docstrings
        self.remove_literal_expression_statements = remove_literal_expression_statements

    def __repr__(self):
        return 'RemoveLiteralStatementsOptions(remove_module_docstring=%r, remove_function_docstrings=%r, remove_class_docstrings=%r, remove_literal_expression_statements=%r)' % (
            self.remove_module_docstring, self.remove_function_docstrings, self.remove_class_docstrings, self.remove_literal_expression_statements
        )

    def __nonzero__(self):
        return any((self.remove_module_docstring, self.remove_function_docstrings, self.remove_class_docstrings, self.remove_literal_expression_statements))

    def __bool__(self):
        return self.__nonzero__()
