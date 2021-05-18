# Extended Tests

The tests in this directory take a very long time and require a specific environment to run.

## test_unparse_env.py

Tests module unparsing of every file in the active python `sys.path`. If a minified unparsed module doesn't
parse back into the original module, that test fails.

## test_regrtest.py

Minifies and executes files listed in a test manifest. Multiple combinations of options are tested, with additional
options specified where necessary. A non zero exit code from a minified execution is a test failure.

The `manifests` directory contains manifests for testing the cpython/pypy regression tests on supported python versions.
