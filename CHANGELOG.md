# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.3] - Unreleased
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

[2.1.3]: https://github.com/dflook/python-minifier/compare/2.1.2...HEAD
[2.1.2]: https://github.com/dflook/python-minifier/compare/2.1.1...2.1.2
[2.1.1]: https://github.com/dflook/python-minifier/compare/2.1.0...2.1.1
[2.1.0]: https://github.com/dflook/python-minifier/compare/2.0.0...2.1.0
[2.0.0]: https://github.com/dflook/python-minifier/compare/1.1.0...2.0.0
[1.1.0]: https://github.com/dflook/python-minifier/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/dflook/python-minifier/tree/1.0.0
