# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

:information_source: Note that python-minifier depends on the python interpreter for parsing source code,
and will output source code compatible with the version of the interpreter it is run with.

This means that if you minify code written for Python 3.11 using python-minifier running with Python 3.12,
the minified code may only run with Python 3.12.

## [Unreleased] - Work in Progress

### Added Unreleased

- Python 3.14 support (work in progress), including:
  - PEP 750 Template strings (t-strings)
  - Exception handling without parentheses
  - PEP 649 Deferred annotation evaluation

## [3.0.0] - 2025-08-13

### Fixed 3.0.0

- Better support of unicode on platforms that do not use UTF-8 as the default encoding.
  This should fix issues with minifying files on Windows, and possibly other platforms with very old Python versions.

  If you are still using Python 2.7 this could be a breaking change - the pyminify command is unchanged, but the `minify()` function now returns unicode strings.

## [2.11.3] - 2024-11-12

### Fixed 2.11.3

- The special behaviour of assignment expression target binding inside comprehensions was not correctly implemented.

  This could lead to the analysed scope of these variables being incorrect and the variable being renamed to a name that was
  already in scope.

## [2.11.2] - 2024-10-03

### Fixed 2.11.2

- Using the positional only parameter separator `/` in method definitions could cause the following parameter to be
  incorrectly renamed in place, which could lead to failure if the method was called with that parameter as a keyword argument.
  This has been fixed.

## [2.11.1] - 2024-09-29

### Fixed 2.11.1

- Using the `--remove-class-attribute-annotations` option together with `--rename-globals` was incorrectly causing
  class attributes to be renamed. Both of these options are unsafe for arbitrary code and are disabled by default
  but this was not the intended behavior, and has been fixed.

## [2.11.0] - 2024-09-26

### Added 2.11.0

- Python 3.13 support, including:
  - PEP 696 Type parameter defaults

## [2.10.0] - 2024-09-15

### Added 2.10.0

- Python 3.12 support, including:
  - PEP 695 Type parameter syntax
  - PEP 701 Improved f-strings

- A new transform to remove the brackets when instantiating and raising built-in exceptions, which is enabled by default.
  e.g.

   ```python
  def a():
      raise ValueError()
  ```

  Will be minified to:

  ```python
  def a():raise ValueError
  ```

  The raise statement automatically instantiates classes derived from Exception, so the brackets are not required.

- A new constant folding transform, which is enabled by default.
  This will evaluate simple expressions when minifying, e.g.

  ```python
  SECONDS_IN_A_DAY = 60 * 60 * 24
  ```

  Will be minified to:

  ```python
  SECONDS_IN_A_DAY=86400
  ```

### Changed 2.10.0

- Annotation removal is now more configurable, with separate options for:
  - Removal of variable annotations (`--no-remove-variable-annotations`)
  - Removal of function return annotations (`--no-remove-return-annotations`)
  - Removal of function argument annotations (`--no-remove-argument-annotations`)
  - Removal of class attribute annotations (`--remove-class-attribute-annotations`)

  The default behavior has changed, with class attribute annotations no longer removed by default.
  These are increasingly being used at runtime, and removing them can cause issues.

### Fixed 2.10.0

- Fixed various subtle issues with renaming of names that overlap class scope.

## [2.9.0] - 2023-05-01

### Added 2.9.0

- A new transform to remove `return` statements that are not required, which is enabled by default.
  e.g.

   ```python
  def important(a):
      if a > 3:
          return a
      if a < 2:
          return None
      a.adjust(1)
      return None
  ```

  Will be minified to:

  ```python
  def important(a):
      if a > 3:
          return a
      if a < 2:
          return
      a.adjust(1)
  ```

- The f-string debug specifier will now be used where possible, e.g. `f'my_var={my_var!r}'` will be minified to `f'{my_var=}'`.
  The debug specifier should now be preserved where it is used in the input source.

- Many small improvements to minification to be more precise about where whitespace or parentheses required
  - Thanks [luk3yx](https://github.com/luk3yx) for improving whitespace in relative import statements.
  - A generator as the sole argument to a function call is no longer wrapped in parentheses
  - float literals can use a more compact scientific notation
  - Many more subtle improvements

## [2.8.1] - 2023-03-15

### Fixed 2.8.1

- A bug shortening names in the iterable of a comprehension when the original name was also used as a target in the comprehension
  e.g. `def f(x): return [x for x in x]` would be incorrectly minified to `def f(x):return[A for A in A]`, instead of `def f(x):return[A for A in x]`.

## [2.8.0] - 2022-12-27

### Added 2.8.0

- New transforms that together work similarly to Python's [-O option](https://docs.python.org/3/using/cmdline.html#cmdoption-O)
  - Remove asserts, which removes assert statements and is disabled by default
  - Remove debug, which removes any `if` block that tests `__debug__ is True` and is disabled by default

### Changed 2.8.0

- When minifying a directory, files ending with '.pyw' will now be minified.

## [2.7.0] - 2022-10-27

### Added 2.7.0

- Python 3.11 support, including exception groups syntax

### Changed 2.7.0

- Improved detection of dataclasses when using the remove annotations transform,
  which suppresses removal of annotations for those classes

### Fixed 2.7.0

- Renamed `nonlocal` names could be incorrect if the name isn't local in the immediate parent function scope.
  (or it was bound in the immediate parent, but after the definition of the nested scope)

## [2.6.0] - 2022-04-10

### Added 2.6.0

- A new option to preserve the shebang line from the source file, which is enabled by default
- More flexible file processing options for the `pyminify` command:
  - A new `--output` argument for writing the minified output to a file without having to use shell redirection
  - A new `--in-place` option which overwrites the specified path with the minified output
  - `path` arguments may be directories, which minifies all *.py files below that directory
  - Multiple `path` arguments may be specified, which will all be minified
- Type information is included in the package to enable type checking of the public functions

### Fixed 2.6.0

- No longer assumes files read from stdin are utf-8.

## [2.5.0] - 2021-10-06

### Added 2.5.0

- Support for Python 3.10, including pattern matching syntax

### Changed 2.5.0

- Makes better decisions about when renaming is space efficient

## [2.4.2] - 2021-06-28

### Fixed 2.4.2

- Rare Exceptions when encountering empty f-string str parts
- Missing required parentheses in return statements for iterable unpacking in python <3.8
- Missing parentheses in some complex dict expansions

### Removed 2.4.2

- Python 2.6 support

## [2.4.1] - 2020-10-17

### Changed 2.4.1

- When the remove annotation transformation is enabled, annotations are preserved on detected usage of TypedDict or NamedTuple

## [2.4.0] - 2020-10-15

### Added 2.4.0

- Support for Python 3.9, including:
  - PEP 614 - Relaxing Grammar Restrictions On Decorators

## [2.3.2] - 2020-10-11

### Fixed 2.3.2

- await keyword can now be used in f-string expression parts

## [2.3.1] - 2020-05-04

### Fixed 2.3.1

- `args` and `kwargs` could have been renamed incorrectly in Python 2.6/2.7, particularly when reminifying a file

## [2.3.0] - 2019-11-18

### Added 2.3.0

- Optional source transform:
  - convert positional arguments to normal arguments, enabled by default

### Fixed 2.3.0

- Unnecessary spaces after ',' in tuple values
- Removing annotations for positional-only arguments (Thanks [luk3yx](https://github.com/luk3yx)!)
- `--no-remove-annotations` argument to `pyminify` had no effect

## [2.2.1] - 2019-11-03

### Fixed 2.2.1

- Unnecessary spaces after ';' in minified output have been removed
- Fixed PendingDeprecationWarnings

## [2.2.0] - 2019-10-27

### Added 2.2.0

- Support for Python 3.8 language features:
  - Assignment expressions
  - Positional parameters
  - f-string = specifier

### Changed 2.2.0

- Removed unnecessary parenthesis around yield statements

### Fixed 2.2.0

- Reading from stdin

## [2.1.2] - 2019-06-27

### Changed 2.1.2

- Improved renaming performance

## [2.1.1] - 2019-04-07

### Changed 2.1.1

- Removed redundant parentheses from comprehension iteration values

## [2.1.0] - 2019-01-24

### Added 2.1.0

- Optional source transforms:
  - remove object base, enabled by default

### Changed 2.1.0

- Return statements no longer wrap tuples in extraneous parentheses
- Duplicated literals are only raised to the lowest common function namespace

## [2.0.0] - 2019-01-13

### Added 2.0.0

- Optional source transformations:
  - Rename locals, enabled by default
  - Rename globals, disabled by default

### Changed 2.0.0

- Minified code will no longer have leading or trailing whitespace
- Generated names for hoisted literals will have an initial underscore if rename globals is disabled
- Suites of simple statements won't create an indented block
- All transforms are now functional on all supported python versions
- The module docstring is not removed by the remove literal statements transformation if there is a name bound for it

### Fixed 2.0.0

- Python 3.7 dataclass field annotations are no longer removed when the remove annotation transformation is enabled

## [1.1.0] - 2018-06-05

### Added 1.1.0

- Optional source transformations:
  - Combine import statements
  - Remove annotations
  - Remove pass statements
  - Remove unused literals, including docstrings
  - Move duplicated literals into module level variables

## [1.0.0] - 2018-05-25

### Added 1.0.0

- python-minifier package
- pyminify command

[3.0.0]: https://github.com/dflook/python-minifier/compare/2.11.3...3.0.0
[2.11.3]: https://github.com/dflook/python-minifier/compare/2.11.2...2.11.3
[2.11.2]: https://github.com/dflook/python-minifier/compare/2.11.1...2.11.2
[2.11.1]: https://github.com/dflook/python-minifier/compare/2.11.0...2.11.1
[2.11.0]: https://github.com/dflook/python-minifier/compare/2.10.0...2.11.0
[2.10.0]: https://github.com/dflook/python-minifier/compare/2.9.0...2.10.0
[2.9.0]: https://github.com/dflook/python-minifier/compare/2.8.1...2.9.0
[2.8.1]: https://github.com/dflook/python-minifier/compare/2.8.0...2.8.1
[2.8.0]: https://github.com/dflook/python-minifier/compare/2.7.0...2.8.0
[2.7.0]: https://github.com/dflook/python-minifier/compare/2.6.0...2.7.0
[2.6.0]: https://github.com/dflook/python-minifier/compare/2.5.0...2.6.0
[2.5.0]: https://github.com/dflook/python-minifier/compare/2.4.2...2.5.0
[2.4.2]: https://github.com/dflook/python-minifier/compare/2.4.1...2.4.2
[2.4.1]: https://github.com/dflook/python-minifier/compare/2.4.0...2.4.1
[2.4.0]: https://github.com/dflook/python-minifier/compare/2.3.2...2.4.0
[2.3.2]: https://github.com/dflook/python-minifier/compare/2.3.1...2.3.2
[2.3.1]: https://github.com/dflook/python-minifier/compare/2.3.0...2.3.1
[2.3.0]: https://github.com/dflook/python-minifier/compare/2.2.1...2.3.0
[2.2.1]: https://github.com/dflook/python-minifier/compare/2.2.0...2.2.1
[2.2.0]: https://github.com/dflook/python-minifier/compare/2.1.2...2.2.0
[2.1.2]: https://github.com/dflook/python-minifier/compare/2.1.1...2.1.2
[2.1.1]: https://github.com/dflook/python-minifier/compare/2.1.0...2.1.1
[2.1.0]: https://github.com/dflook/python-minifier/compare/2.0.0...2.1.0
[2.0.0]: https://github.com/dflook/python-minifier/compare/1.1.0...2.0.0
[1.1.0]: https://github.com/dflook/python-minifier/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/dflook/python-minifier/tree/1.0.0
