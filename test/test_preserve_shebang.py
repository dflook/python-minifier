from python_minifier import minify


def test_no_preserve_shebang():
    source = '''#! hello this is my shebang
a=0'''

    minified = '''a=0'''

    actual = minify(source, preserve_shebang=False)
    assert actual == minified


def test_no_preserve_shebang_bytes():
    source = b'''#! hello this is my shebang
a=0'''

    minified = '''a=0'''

    actual = minify(source, preserve_shebang=False)
    assert actual == minified


def test_preserve_shebang():
    source = '''#! hello this is my shebang
a=0'''

    actual = minify(source, preserve_shebang=True)
    assert actual == source


def test_preserve_shebang_bytes():
    source = b'''#! hello this is my shebang
a=0'''

    actual = minify(source, preserve_shebang=True)
    assert actual == source.decode()


def test_no_shebang():
    source = '''a=0'''

    actual = minify(source, preserve_shebang=True)
    assert actual == source


def test_no_shebang_bytes():
    source = b'''a=0'''

    actual = minify(source, preserve_shebang=True)
    assert actual == source.decode()
