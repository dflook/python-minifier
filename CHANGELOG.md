# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

:information_source: Note that python-minifier depends on the python interpreter for parsing source code,
and will output source code compatible with the version of the interpreter it is run with.

This means that if you minify code written for Python 3.11 using python-minifier running with Python 3.12,
the minified code may only run with Python 3.12.

## [2.11.0] - 2024-09-26

### Added
- Python 3.13 support, including:
    - PEP 696 Type parameter defaults

## [2.10.0] - 2024-09-15

### Added
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

### Changed
- Annotation removal is now more configurable, with separate options for:
    - Removal of variable annotations (`--no-remove-variable-annotations`)
    - Removal of function return annotations (`--no-remove-return-annotations`)
    - Removal of function argument annotations (`--no-remove-argument-annotations`)
    - Removal of class attribute annotations (`--remove-class-attribute-annotations`)

  The default behavior has changed, with class attribute annotations no longer removed by default.
  These are increasingly being used at runtime, and removing them can cause issues.

### Fixed
- Fixed various subtle issues with renaming of names that overlap class scope.

## [2.9.0] - 2023-05-01

### Added
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

### Fixed
- A bug shortening names in the iterable of a comprehension when the original name was also used as a target in the comprehension
  e.g. `def f(x): return [x for x in x]` would be incorrectly minified to `def f(x):return[A for A in A]`, instead of `def f(x):return[A for A in x]`.

## [2.8.0] - 2022-12-27

### Added
- New transforms that together work similarly to Python's [-O option](https://docs.python.org/3/using/cmdline.html#cmdoption-O)
    - Remove asserts, which removes assert statements and is disabled by default
    - Remove debug, which removes any `if` block that tests `__debug__ is True` and is disabled by default

### Changed
- When minifiying a directory, files ending with '.pyw' will now be minified.

## [2.7.0] - 2022-10-27

### Added
- Python 3.11 support, including exception groups syntax

### Changed
- Improved detection of dataclasses when using the remove annotations transform, 
  which suppresses removal of annotations for those classes

### Fixed
- Renamed `nonlocal` names could be incorrect if the name isn't local in the immediate parent function scope.
  (or it was bound in the immediate parent, but after the definition of the nested scope)

## [2.6.0] - 2022-04-10

### Added
- A new option to preserve the shebang line from the source file, which is enabled by default
- More flexible file processing options for the `pyminify` command:
    - A new `--output` argument for writing the minified output to a file without having to use shell redirection
    - A new `--in-place` option which overwrites the specified path with the minified output
    - `path` arguments may be directories, which minifies all *.py files below that directory
    - Multiple `path` arguments may be specified, which will all be minified
- Type information is included in the package to enable type checking of the public functions

### Fixed
- No longer assumes files read from stdin are utf-8.

## [2.5.0] - 2021-10-06

### Added
- Support for Python 3.10, including pattern matching syntax

### Changed
- Makes better decisions about when renaming is space efficient

## [2.4.2] - 2021-06-28

### Fixed
- Rare Exceptions when encountering empty f-string str parts
- Missing required parentheses in return statements for iterable unpacking in python <3.8
- Missing parentheses in some complex dict expansions

### Removed
- Python 2.6 support

## [2.4.1] - 2020-10-17

### Changed
- When the remove annotation transformation is enabled, annotations are preserved on detected usage of TypedDict or NamedTuple

## [2.4.0] - 2020-10-15

### Added
- Support for Python 3.9, including:
    - PEP 614 - Relaxing Grammar Restrictions On Decorators

## [2.3.2] - 2020-10-11

### Fixed
- await keyword can now be used in f-string expression parts

## [2.3.1] - 2020-05-04

### Fixed
- `args` and `kwargs` could have been renamed incorrectly in Python 2.6/2.7, particularly when reminifying a file

## [2.3.0] - 2019-11-18

### Added
- Optional source transform:
    - convert positional arguments to normal arguments, enabled by default

### Fixed
- Unnecessary spaces after ',' in tuple values
- Removing annotations for positional-only arguments (Thanks [luk3yx](https://github.com/luk3yx)!)
- `--no-remove-annotations` argument to `pyminify` had no effect

## [2.2.1] - 2019-11-03

### Fixed
- Unnecessary spaces after ';' in minified output have been removed
- Fixed PendingDeprecationWarnings

## [2.2.0] - 2019-10-27
### Added
- Support for Python 3.8 language features:
    - Assignment expressions
    - Positional parameters
    - f-string = specifier

### Changed
- Removed unnecessary parenthesis around yield statements

### Fixed
- Reading from stdin

## [2.1.2] - 2019-06-27
### Changed
- Improved renaming performance

## [2.1.1] - 2019-04-07
### Changed
- Removed redundant parentheses from comprehension iteration values

## [2.1.0] - 2019-01-24
### Added
- Optional source transforms:
    - remove object base, enabled by default

### Changed
- Return statements no longer wrap tuples in extraneous parentheses
- Duplicated literals are only raised to the lowest common function namespace

## [2.0.0] - 2019-01-13
### Added
- Optional source transformations:
    - Rename locals, enabled by default
    - Rename globals, disabled by default

### Changed
- Minified code will no longer have leading or trailing whitespace
- Generated names for hoisted literals will have an initial underscore if rename globals is disabled
- Suites of simple statements won't create an indented block
- All transforms are now functional on all supported python versions
- The module docstring is not removed by the remove literal statements transformation if there is a name bound for it

### Fixed
- Python 3.7 dataclass field annotations are no longer removed when the remove annotation transformation is enabled

## [1.1.0] - 2018-06-05
### Added
- Optional source transformations:
    - Combine import statements
    - Remove annotations
    - Remove pass statements
    - Remove unused literals, including docstrings
    - Move duplicated literals into module level variables

## [1.0.0] - 2018-05-25
### Added
- python-minifier package
- pyminify command

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
