import itertools

from python_minifier.transforms.name_generator import name_filter

def test_name_generator():

    predefined = ['hi', 'oh', 'AA']

    ng = name_filter(predefined)

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

    # Check predefined names not returned
    for name in predefined:
        assert name not in names
