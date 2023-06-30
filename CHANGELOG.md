# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.3] - 2023-06-30

### Fixed

- Fix speed calculation for `rcli export` command, [PR-61](https://github.com/reductstore/reduct-cli/pull/61)

## [0.8.2] - 2023-06-05

### Changed

- Use `reduct-py~=1.4`, [PR-60](https://github.com/reductstore/reduct-cli/pull/60)

## [0.8.1] - 2023-03-10

### Fixed

- Exception in `bucket create` command, [PR-57](https://github.com/reductstore/reduct-cli/pull/57)

## [0.8.0] - 2023-03-08

### Added

- `--with-metadata` flag for `rcli export folder` command to export metadata
  along with the records, [PR-55](https://github.com/reductstore/reduct-cli/pull/55)
- Support integers for --start and --stop options of rcli export
  commands, [PR-56](https://github.com/reductstore/reduct-cli/pull/56)

## [0.7.0] - 2023-02-19

### Added

- Wildcard support for `--entries` option in `rcli export`
  command, [PR-51](https://github.com/reductstore/reduct-cli/pull/51)
- Stop creating folder with bucket name
  in `rcli export folder`, [PR-52](https://github.com/reductstore/reduct-cli/pull/52)

### Fixed

- Fix expired query error, [PR-50](https://github.com/reductstore/reduct-cli/pull/50)

## [0.6.0] - 2023-02-05

### Added

- Copy labels and content type in `rcli export bucket`
  command, [PR-43](https://github.com/reductstore/reduct-cli/pull/43)
- Guess extension from content type or force it with `--ext` option in `rcli export folder`
  command, [PR-45](https://github.com/reductstore/reduct-cli/pull/45)
- Options `--exclude` and `--include` to `rcli export`
  commands, [PR-46](https://github.com/reductstore/reduct-cli/pull/46)

### Changed

- Move `mirror` command to `export command`, [PR-42](https://github.com/reductstore/reduct-cli/pull/42)

### Deprecated

- `mirror` command, [PR-42](https://github.com/reductstore/reduct-cli/pull/42)

## [0.5.0] - 2023-01-20

### Added:

- Support `Z` designator for UTC timestamps in `rcli export` and `rcli mirror`
  commands, [PR-33](https://github.com/reductstore/reduct-cli/pull/33)
- Communication timeout as a global option, [PR-34](https://github.com/reductstore/reduct-cli/pull/34)
- `--entries` option to `rcli mirror` and `rcli export`
  commands, [PR-36](https://github.com/reductstore/reduct-cli/pull/36)
- URL validation to `alias add` command, [PR-37](https://github.com/reductstore/reduct-cli/pull/37)
- Graceful handling of `SIGINT` and `SIGTERM` signals, [PR-38](https://github.com/reductstore/reduct-cli/pull/38)

### Fixed:

- 409 HTTP error in `rcli mirror`, [PR-27](https://github.com/reductstore/reduct-cli/pull/27)

## [0.4.0] - 2022-12-26

### Added:

- `rcli export folder` to export data from a bucket to a folder on local
  machine, [PR-25](https://github.com/reductstore/reduct-cli/pull/25)

### Changed:

- Improve documentation, [PR-21](https://github.com/reductstore/reduct-cli/pull/21)
- Update documentation after rebranding, [PR-23](https://github.com/reductstore/reduct-cli/pull/23)

## [0.3.0] - 2022-12-07

### Added:

- `rcli mirror` to copy data from a bucket to another
  one, [PR-18](https://github.com/reductstore/reduct-cli/pull/18)
- `rcli token` to manage API tokens, [PR-20](https://github.com/reductstore/reduct-cli/pull/20)

## [0.2.0]

### Added:

- `rcli` alias for `reduct-cli`, [PR-10](https://github.com/reductstore/reduct-cli/pull/10)
- Options for server URL and API token to alias add
  command, [PR-11](https://github.com/reductstore/reduct-cli/pull/11)
- `rcli bucket ls` to list buckets, [PR-13](https://github.com/reductstore/reduct-cli/pull/13)
- `rcli bucket show` to browse a bucket, [PR-14](https://github.com/reductstore/reduct-cli/pull/14)
- `rcli bucket create` to create a bucket, [PR-15](https://github.com/reductstore/reduct-cli/pull/15)
- `rcli bucket update` to update bucket settings, [PR-16](https://github.com/reductstore/reduct-cli/pull/16)
- `rcli bucket rm` to remove a bucket, [PR-17](https://github.com/reductstore/reduct-cli/pull/17)

### Changed:

- Improve output of server status command, [PR-12](https://github.com/reductstore/reduct-cli/pull/12)

## [0.1.0] - 2022-10-24

### Added:

- Add alias commands: add, remove, show, [PR-6](https://github.com/reductstore/reduct-cli/pull/6)
- Add `server status` command to check server's status, [PR-9](https://github.com/reductstore/reduct-cli/pull/9)

### Changed:

- Make alias command more idiomatic, [PR-7](https://github.com/reductstore/reduct-cli/pull/7)

## [0.0.0] - 2022-10-17

- Init release

[Unreleased]: https://github.com/reductstore/reduct-cli/compare/v0.8.3...HEAD

[0.8.3]: https://github.com/reductstore/reduct-cli/compare/v0.8.2...v0.8.3

[0.8.2]: https://github.com/reductstore/reduct-cli/compare/v0.8.1...v0.8.2

[0.8.1]: https://github.com/reductstore/reduct-cli/compare/v0.8.0...v0.8.1

[0.8.0]: https://github.com/reductstore/reduct-cli/compare/v0.7.0...v0.8.0

[0.7.0]: https://github.com/reductstore/reduct-cli/compare/v0.6.0...v0.7.0

[0.6.0]: https://github.com/reductstore/reduct-cli/compare/v0.5.0...v0.6.0

[0.5.0]: https://github.com/reductstore/reduct-cli/compare/v0.4.0...v0.5.0

[0.4.0]: https://github.com/reductstore/reduct-cli/compare/v0.3.0...v0.4.0

[0.3.0]: https://github.com/reductstore/reduct-cli/compare/v0.2.0...v0.3.0

[0.2.0]: https://github.com/reductstore/reduct-cli/compare/v0.1.0...v0.2.0

[0.1.0]: https://github.com/reductstore/reduct-cli/compare/v0.0.0...v0.1.0

[0.0.0]: https://github.com/reductstore/reduct-cli/compare/tag/v0.0.0
