from python_minifier import minify

with open('snippet.py', 'rb') as f:
    source = f.read()

minified = minify(source)

with open('minified.py', 'w', encoding='ascii', errors='backslashreplace') as f:
    f.write(minified)
