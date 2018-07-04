def compile(source: "something compilable",
            filename: "where the compilable thing comes from",
            mode: "A string annotation"):
    a: int = 1
    b: str

    def inner():
        nonlocal b
        b = 'hello'

    inner()
    print(b)

compile(None, None, None)
