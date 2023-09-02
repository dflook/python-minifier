class RemoveLiteralStatementsOptions:

    remove_module_docstring: bool
    remove_function_docstrings: bool
    remove_class_docstrings: bool
    remove_literal_expression_statements: bool

    def __init__(self,
                 remove_module_docstring: bool = ...,
                 remove_function_docstrings: bool = ...,
                 remove_class_docstrings: bool = ...,
                 remove_literal_expression_statements: bool = ...):
        ...

    def __repr__(self) -> str: ...
    def __nonzero__(self) -> bool: ...
    def __bool__(self) -> bool: ...
