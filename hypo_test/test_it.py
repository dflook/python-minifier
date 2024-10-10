import ast

from datetime import timedelta

from hypothesis import HealthCheck, Verbosity, given, note, settings

from python_minifier.ast_compare import compare_ast
from python_minifier.ast_printer import print_ast
from python_minifier.expression_printer import ExpressionPrinter
from python_minifier.module_printer import ModulePrinter
from python_minifier.rename.mapper import add_parent
from python_minifier.transforms.constant_folding import FoldConstants

from .expressions import Expression
from .folding import FoldableExpression
from .module import Module, TypeAlias
from .patterns import Pattern


@given(node=Expression())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=1), max_examples=100, suppress_health_check=[HealthCheck.too_slow]) #verbosity=Verbosity.verbose
def test_expression(node):
    assert isinstance(node, ast.AST)

    note(ast.dump(node))
    printer = ExpressionPrinter()
    code = printer(node)
    note(code)
    compare_ast(node, ast.parse(code, 'test_expression', 'eval'))


@given(node=Module())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=1), max_examples=100, suppress_health_check=[HealthCheck.too_slow], verbosity=Verbosity.verbose)
def test_module(node):
    assert isinstance(node, ast.Module)

    note(ast.dump(node))
    printer = ModulePrinter()
    code = printer(node)
    note(code)
    compare_ast(node, ast.parse(code, 'test_module'))


@given(node=Pattern())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=2), max_examples=100, verbosity=Verbosity.verbose)
def test_pattern(node):

    module = ast.Module(
        body=[ast.Match(subject=ast.Constant(value=None),
                        cases=[
                            ast.match_case(
                                pattern=node,
                                guard=None,
                                body=[ast.Pass()]
                            )
                        ])],
        type_ignores=[]
    )

    printer = ModulePrinter()
    code = printer(module)
    note(code)
    compare_ast(module, ast.parse(code, 'test_pattern'))

@given(node=FoldableExpression())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=1), max_examples=1000, suppress_health_check=[HealthCheck.too_slow]) #verbosity=Verbosity.verbose
def test_folding(node):
    assert isinstance(node, ast.AST)
    note(print_ast(node))

    add_parent(node)

    constant_folder = FoldConstants()

    # The constant folder asserts the value is correct
    constant_folder(node)

@given(node=TypeAlias())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=2), max_examples=100, verbosity=Verbosity.verbose)
def test_type_alias(node):

    module = ast.Module(
        body=[node],
        type_ignores=[]
    )

    printer = ModulePrinter()
    code = printer(module)
    note(code)
    compare_ast(module, ast.parse(code, 'test_type_alias'))

@given(node=TypeAlias())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=2), max_examples=100, verbosity=Verbosity.verbose)
def test_function_type_param(node):

    module = ast.Module(
        body=[ast.FunctionDef(
            name='test',
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[ast.Pass()],
            type_params=node.type_params,
            decorator_list=[],
            returns=None
        )],
        type_ignores=[]
    )

    printer = ModulePrinter()
    code = printer(module)
    note(code)
    compare_ast(module, ast.parse(code, 'test_function_type_param'))
