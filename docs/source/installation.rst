Installation
============

To install python-minifier use pip:

.. code-block:: bash

    $ pip install python-minifier

Note that python-minifier depends on the python interpreter for parsing source code,
and outputs source code compatible with the version of the interpreter it is run with.

This means that if you minify code written for Python 3.6 using python-minifier running with Python 3.12,
the minified code may only run with Python 3.12.

python-minifier runs with and can minify code written for Python 2.7 and Python 3.3 to 3.14.
