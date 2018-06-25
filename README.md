# Python Minifier

Transforms Python source code into it's most compact representation.

python-minifier supports Python 2.6 to 2.7 and Python 3.3 to 3.7.

As an example, the following python source:

```python
import ast

from python_minifier.miniprinter import MiniPrinter
from python_minifier.ast_compare import AstCompare

class UnstableMinification(Exception):
    def __init__(self, original, minified, exception):
        self.original = original
        self.minified = minified
        self.exception = exception

    def __str__(self):
        return str(self.exception)

def minify(source):

    code = ast.parse(source)
    minifier = MiniPrinter()

    minifier.visit(code)

    try:
        # Check that the minified code is identical to the original
        minified_code = ast.parse(minifier.code)
        comparer = AstCompare()
        comparer.compare(code, minified_code)
    except Exception as exception:
        raise UnstableMinification(source, minifier.code, exception)

    return minifier.code
```

Becomes:

```python
import ast
from python_minifier.miniprinter import MiniPrinter
from python_minifier.ast_compare import AstCompare
class UnstableMinification(Exception):
    def __init__(self,original,minified,exception):
        self.original=original;self.minified=minified;self.exception=exception
    def __str__(self):return str(self.exception)
def minify(source):
    code=ast.parse(source);minifier=MiniPrinter();minifier.visit(code)
    try:
        minified_code=ast.parse(minifier.code);comparer=AstCompare();comparer.compare(code,minified_code)
    except Exception as exception:
        raise UnstableMinification(source,minifier.code,exception)
    return minifier.code
```

## Why?

AWS Cloudformation templates may have AWS lambda function source code embedded in them, but only if the function is less 
than 4KiB. I wrote this package so I could write python normally and still embed the module in a template.

## Installation

To install python-minifier use pip:

```bash
$ pip install python-minifier
```

Note that python-minifier depends on the python interpreter for parsing source code, 
so install using a version of python appropriate for your source.

python-minifier runs with and can minify code written for Python 2.6 to 2.7 and Python 3.3 to 3.7.

## Usage

To minify a source file, and write the minified module to stdout:

```bash
$ pyminify hello.py
```

There is also an API. The same example would look like:

```python
import python_minifier

with open('hello.py') as f:
    print(python_minifier.minify(f.read()))
```

## License

Available under the MIT License. Full text is in the [LICENSE](LICENSE) file.

Copyright (c) 2018 Daniel Flook
