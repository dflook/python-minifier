import ast

import pytest

from python_minifier.ast_compare import compare_ast
from python_minifier.rename import add_namespace, bind_names, resolve_names
from python_minifier.transforms.remove_unused_platform_options import (
    RemoveUnusedPlatformOptions,
)
from python_minifier.transforms.remove_unused_platforms import RemoveUnusedPlatforms


def remove_unused_platform(source):
    module = ast.parse(source, "remove_unused_platform")

    add_namespace(module)
    bind_names(module)
    resolve_names(module)
    return RemoveUnusedPlatforms(
        RemoveUnusedPlatformOptions(
            platform_test_key=RemoveUnusedPlatformOptions.platform_test_key,
            platform_preserve_value=RemoveUnusedPlatformOptions.platform_preserve_value,
        )
    )(module)


def test_empty_module_remove_platform_no_equals__expect_no_change():
    source = "if _PLATFORM: pass"
    expected = "if _PLATFORM: pass"

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_empty_module_remove_platform_equals_non_target___expect_gone():
    source = 'if _PLATFORM == "bsd": pass'
    expected = ""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_empty_module_remove_platform_equals_non_target_reverse_test___expect_gone():
    source = 'if "bsd" == _PLATFORM: pass'
    expected = ""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_empty_module_remove_platform_equals_target___expect_flattened():
    source = 'if _PLATFORM == "linux": x=1'
    expected = "x=1"

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_platform_simple_non_target_module__expect_removed():
    source = """
import collections
if _PLATFORM == "bsd": pass
a = 1
if _PLATFORM == "bsd": pass
"""

    expected = """import collections
a=1"""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_platform_simple_target_module__expect_flattened():
    source = """
import collections
if _PLATFORM == "linux": a = 1
b = 2
if _PLATFORM == "linux": c = 3
"""

    expected = """import collections
a = 1
b = 2
c = 3
"""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_do_not_remove_nested_if():
    """
    The intention is only to remove module level statements to keep the
    behaviour simple and to encourage not having highly nested platform
    specific code (see PEP20).
    """

    source = """
if True:
    if _PLATFORM == "linux": pass
"""

    expected = """if True:
    if _PLATFORM == "linux": pass"""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_do_not_remove_from_class():
    """
    PEP20
    """

    source = """class A:
    if _PLATFORM == "linux": pass
    a = 1
    if _PLATFORM == "linux": pass
    def b():
        if _PLATFORM == "linux": pass
        return 1        
"""
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_remove_platform_multi_target_if_module__expect_non_target_removed():
    source = """
import collections
if _PLATFORM == "linux": pass
a = 1
if _PLATFORM == "linux": pass

if _PLATFORM == "bsd":
    class A:
        pass

if _PLATFORM == "win":
    class B:
        pass

if _PLATFORM == "linux":
    class C:
        pass

"""

    expected = """import collections
a = 1
class C:
    pass"""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


@pytest.mark.parametrize(
    "source",
    [
        # Target Platform in elif
        """
if _PLATFORM == "bsd": 
    class A:
        pass

elif _PLATFORM == "win": 
    class B:
        pass

elif _PLATFORM == "linux": 
    class C:
        pass
else:
    raise NotImplemented(_PLATFORM)

""",
        # Target Platform in if
        """
if _PLATFORM == "linux": 
    class C:
        pass

elif _PLATFORM == "win": 
    class B:
        pass

elif _PLATFORM == "bsd": 
    class A:
        pass
else:
    raise NotImplemented(_PLATFORM)

""",
        # Target Platform is else
        """
if _PLATFORM == "bsd": 
    class A:
        pass

elif _PLATFORM == "win": 
    class B:
        pass

elif _PLATFORM == "other": 
    raise NotImplemented(_PLATFORM)    
    
else:
    class C:
        pass
""",
    ],
)
def test_remove_platform_multi_target_elif_module__expect_non_target_removed(source):
    expected = """class C:
    pass"""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


@pytest.mark.parametrize(
    "source",
    [
        # "in" is not currently supported, irrespective of where
        # it is in the if/elif block.
        """
if _PLATFORM == "bsd": 
    class A:
        pass

elif _PLATFORM in ["win", "mac"]: 
    class B:
        pass

elif _PLATFORM == "linux": 
    class C:
        pass
else:
    raise NotImplemented(_PLATFORM)

""",
        # "in" is not currently supported, irrespective of where
        # it is in the if/elif block.
        """
if _PLATFORM == "bsd": 
    class A:
        pass

elif _PLATFORM == "win": 
    class B:
        pass

elif _PLATFORM in ["linux"]: 
    class C:
        pass
else:
    raise NotImplemented(_PLATFORM)

""",
        # any non-platform tests will also cause the block to be
        # left along
        """
if _PLATFORM == "bsd": 
    class A:
        pass

elif some_variable == 23: 
    class D:
        pass

elif _PLATFORM == "win": 
    class B:
        pass

elif _PLATFORM == "linux": 
    class C:
        pass
else:
    raise NotImplemented(_PLATFORM)

""",
    ],
)
def test_unsupported_if_statements__expect_no_change(source):
    expected = source

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_elif_statements_no_target__expect_gone():
    source = """
if _PLATFORM == "bsd": 
    class A:
        pass

elif _PLATFORM == "win": 
    class B:
        pass
"""

    expected = ""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)


def test_if_statements_results_in_noop__expect_gone():
    source = """
pass
if _PLATFORM == "linux": 
    pass
elif _PLATFORM == "win": 
    class B:
        pass
"""

    expected = ""

    expected_ast = ast.parse(expected)
    actual_ast = remove_unused_platform(source)
    compare_ast(expected_ast, actual_ast)
