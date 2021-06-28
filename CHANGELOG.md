# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

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
