import itertools

from python_minifier.rename.name_generator import name_filter

def test_name_generator():

    ng = name_filter()

    names = set()
    for name in itertools.islice(ng, 10000):
        assert len(name) <= 3
        names.add(name)

    assert len(names) == 10000

    # Check no keywords returned
    assert 'or' not in names

    # Check no builtins returned
    assert 'id' not in names
    assert 'abs' not in names
