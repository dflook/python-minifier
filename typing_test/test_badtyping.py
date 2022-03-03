"""
This should fail type checking
"""

from python_minifier import minify

def test_typing() -> None:

    minify(456,
           remove_pass='yes please'
    )
