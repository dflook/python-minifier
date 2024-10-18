import pytest
import ast
from python_minifier.ast_annotation import add_parent, get_parent, set_parent


def test_add_parent():

    source = '''
class A:
    def b(self):
        pass
'''

    tree = ast.parse(source)

    add_parent(tree)

    assert isinstance(tree, ast.Module)

    assert isinstance(tree.body[0], ast.ClassDef)
    assert get_parent(tree.body[0]) is tree

    assert isinstance(tree.body[0].body[0], ast.FunctionDef)
    assert get_parent(tree.body[0].body[0]) is tree.body[0]

    assert isinstance(tree.body[0].body[0].body[0], ast.Pass)
    assert get_parent(tree.body[0].body[0].body[0]) is tree.body[0].body[0]


def test_no_parent_for_root_node():
    tree = ast.parse('a = 1')
    add_parent(tree)
    with pytest.raises(ValueError):
        get_parent(tree)


def test_no_parent_for_unannotated_node():
    tree = ast.parse('a = 1')
    with pytest.raises(ValueError):
        get_parent(tree.body[0])


def test_replaces_parent_of_given_node():
    tree = ast.parse('a = func()')
    add_parent(tree)
    call = tree.body[0].value
    tree.body[0] = call
    set_parent(call, tree)
    assert get_parent(call) == tree
