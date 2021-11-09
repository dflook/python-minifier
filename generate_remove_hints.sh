#!/bin/sh

wget "https://raw.githubusercontent.com/abarker/strip-hints/master/src/strip_hints/token_list.py"
wget "https://raw.githubusercontent.com/abarker/strip-hints/master/src/strip_hints/strip_hints_main.py"

sed -r -e '\~(from|import) +[^ ]*token_list~{ :a \~^[^\n;)]*[\t ]*(,|$|_|\\)$~{ N; s~\n[\t ]*~ ~; ta; }; r ./token_list.py' -e '; }; ' -- ./strip_hints_main.py \
  | sed -r -e '\~(from|import) +[^ ]*token_list~d; 5,${ \~from __future__ ~d; };' \
  | sed -r -e ' \~if DEBUG: .*[^\]$~d; ' \
  | sed -r -e ' \~print\([^)]*\)[^()]*$~{ s~, end="[^"]*"~~g; } ' \
  | sed -r -e ' \~if version == 2:~{  :a0 N; \~import ~!bz; \~import_hooks~!bz; :a1 \~import_hooks_py3~!{  N; ba1; }; d; }; :z ' \
  | sed -r -e '1a\from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement' \
  | tee ./src/python_minifier/transforms/remove_hints.py

rm -f -- ./token_list.py ./strip_hints_main.py

