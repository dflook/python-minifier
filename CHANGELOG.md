# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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
- Python 3.7 dataclass field annotations are no longer removed when the remove annotation transformation is enabled.

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
- python-minifer package
- pyminify command

[1.2.0]: https://github.com/dflook/python-minifier/compare/1.1.0...HEAD
[1.1.0]: https://github.com/dflook/python-minifier/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/dflook/python-minifier/tree/1.0.0
