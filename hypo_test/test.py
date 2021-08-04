import ast

from datetime import timedelta
from hypothesis import given, settings, Verbosity, note, HealthCheck

from hypo_test.patterns import Pattern
from python_minifier import ModulePrinter
from python_minifier.ast_compare import compare_ast
from python_minifier.expression_printer import ExpressionPrinter
from hypo_test.expressions import Expression
from hypo_test.module import Module

@given(node=Expression())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=1), max_examples=10000, suppress_health_check=[HealthCheck.too_slow]) #verbosity=Verbosity.verbose
def test_expression(node):
    assert isinstance(node, ast.AST)

    note(ast.dump(node))
    printer = ExpressionPrinter()
    printer(node)
    note(printer.code)
    compare_ast(node, ast.parse(printer.code, 'test_expression', 'eval'))


@given(node=Module())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=1), max_examples=10000, suppress_health_check=[HealthCheck.too_slow]) #verbosity=Verbosity.verbose
def test_module(node):
    assert isinstance(node, ast.Module)

    note(ast.dump(node))
    printer = ModulePrinter()
    printer(node)
    note(printer.code)
    compare_ast(node, ast.parse(printer.code, 'test_module'))


@given(node=Pattern())
@settings(report_multiple_bugs=False, deadline=timedelta(seconds=2), max_examples=100000, verbosity=Verbosity.verbose)
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

    print(ast.dump(module))
    printer = ModulePrinter()
    printer(module)
    print(printer.code)
    compare_ast(module, ast.parse(printer.code, 'test_pattern'))
