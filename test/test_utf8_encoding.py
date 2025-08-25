# -*- coding: utf-8 -*-
import python_minifier
import tempfile
import os
import codecs
import sys

def test_minify_utf8_file():
    """Test minifying a Python file with UTF-8 characters not in Windows default encoding."""

    # Create Python source with UTF-8 characters that are not in Windows-1252
    # Using Greek letters, Cyrillic, and mathematical symbols
    source_code = u'''"""
This module contains UTF-8 characters that are not in Windows-1252 encoding:
- Greek: α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
- Cyrillic: а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я
- Mathematical: ∀ ∃ ∈ ∉ ∅ ∞ ∑ ∏ √ ∫ ∇ ∂ ≠ ≤ ≥ ≈ ≡ ⊂ ⊃ ⊆ ⊇
- Arrows: ← → ↑ ↓ ↔ ↕ ↖ ↗ ↘ ↙
"""

def greet_in_greek():
    return u"Γεια σας κόσμος"  # "Hello world" in Greek

def mathematical_formula():
    # Using mathematical symbols in comments
    # ∀x ∈ ℝ: x² ≥ 0
    return u"∑ from i=1 to ∞ of 1/i² = π²/6"

def arrow_symbols():
    directions = {
        u"left": u"←",
        u"right": u"→", 
        u"up": u"↑",
        u"down": u"↓"
    }
    return directions

if __name__ == "__main__":
    print(greet_in_greek())
    print(greet_in_russian())
    print(mathematical_formula())
    print(arrow_symbols())
'''

    # Write to temporary file with UTF-8 encoding
    # Python 2.7 doesn't support encoding parameter, so use binary mode
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as f:
        f.write(source_code.encode('utf-8'))
        temp_file = f.name

    try:
        # Read the file and minify it
        # Python 2.7 doesn't support encoding parameter in open()
        if sys.version_info[0] >= 3:
            with open(temp_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
        else:
            with codecs.open(temp_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

        # This should work - minify the UTF-8 content
        minified = python_minifier.minify(original_content)

        # Verify the minified code still contains the UTF-8 characters
        # On Python 2.7, Unicode characters in string literals are escaped but preserved
        # Test by executing the minified code and checking the actual values
        minified_globals = {}
        exec(minified, minified_globals)

        # The minified code should contain the same functions that return Unicode
        assert 'greet_in_greek' in minified_globals
        assert u"Γεια σας κόσμος" == minified_globals['greet_in_greek']()

        # Test that mathematical symbols are also preserved
        assert 'mathematical_formula' in minified_globals
        assert u"∑ from i=1 to ∞" in minified_globals['mathematical_formula']()

    finally:
        # Clean up
        os.unlink(temp_file)


def test_minify_utf8_file_direct():
    """Test minifying a file directly with UTF-8 characters."""

    # Create Python source with UTF-8 characters
    source_code = u'''# UTF-8 test file
def emoji_function():
    """Function with emoji and special characters: 🐍 ∆ ∑ ∫ ∞"""
    return u"Python is 🐍 awesome! Math symbols: ∆x ≈ 0, ∑∞ = ∞"

class UnicodeClass:
    """Class with unicode: ñ ü ö ä ë ï ÿ"""
    def __init__(self):
        self.message = u"Héllö Wörld with àccénts!"
        
    def get_symbols(self):
        return u"Symbols: ™ © ® ° ± × ÷ ≠ ≤ ≥"
'''

    # Test direct minification
    minified = python_minifier.minify(source_code)

    # Verify UTF-8 characters are preserved by executing the minified code
    minified_globals = {}
    exec(minified, minified_globals)

    # Test that the functions return the correct Unicode strings
    assert u"🐍" in minified_globals['emoji_function']()
    assert u"∆" in minified_globals['emoji_function']()

    # Test the class
    unicode_obj = minified_globals['UnicodeClass']()
    assert u"Héllö" in unicode_obj.message
    assert u"àccénts" in unicode_obj.message
    assert u"™" in unicode_obj.get_symbols()
    assert u"©" in unicode_obj.get_symbols()
