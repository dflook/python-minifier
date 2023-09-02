import ast

from datetime import timedelta
from hypothesis import given, settings, Verbosity, note, HealthCheck

from folding import FoldableExpression
from patterns import Pattern
from python_minifier import ModulePrinter
from python_minifier.ast_compare import compare_ast
from python_minifier.ast_printer import print_ast
from python_minifier.expression_printer import ExpressionPrinter
from expressions import Expression
from module import Module
from python_minifier.rename.mapper import add_parent
from python_minifier.transforms.constant_folding import FoldConstants


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
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=1), max_examples=100, suppress_health_check=[HealthCheck.too_slow]) #verbosity=Verbosity.verbose
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
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=1), max_examples=100000, suppress_health_check=[HealthCheck.too_slow]) #verbosity=Verbosity.verbose
def test_folding(node):
    assert isinstance(node, ast.AST)
    note(print_ast(node))

    add_parent(node)

    constant_folder = FoldConstants()

    # The constant folder asserts the value is correct
    constant_folder(node)
