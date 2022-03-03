import ast
from typing import List, Text, AnyStr, Optional, Any


class UnstableMinification(RuntimeError):
    def __init__(self, exception: Any, source: Any, minified: Any): ...

def minify(
    source: AnyStr,
    filename: Optional[str] = ...,
    remove_annotations: bool = ...,
    remove_pass: bool = ...,
    remove_literal_statements: bool = ...,
    combine_imports: bool = ...,
    hoist_literals: bool = ...,
    rename_locals: bool = ...,
    preserve_locals: Optional[List[Text]] = ...,
    rename_globals: bool = ...,
    preserve_globals: Optional[List[Text]] = ...,
    remove_object_base: bool = ...,
    convert_posargs_to_args: bool = ...,
    preserve_shebang: bool = ...
) -> Text: ...

def unparse(module: ast.Module) -> Text: ...

def awslambda(
    source: AnyStr,
    filename: Optional[Text] = ...,
    entrypoint: Optional[Text] = ...
) -> Text: ...
