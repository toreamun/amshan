# Changelog

## 2.2.0

Requires Python 3.12 or newer. Tested on Python 3.12–3.14 and a pre-release of 3.15.

### Fixed

- The serial and TCP connection factories no longer discard a valid HDLC frame whose last frame check sequence octet is 0x7D (about 1 in 256 frames, also hourly lists) ([#15](https://github.com/toreamun/amshan/pull/15)).
- The HDLC reader recovers after a truncated or broken frame: frames that followed it are no longer lost, only returned a little later ([#16](https://github.com/toreamun/amshan/pull/16)).

### Changed

- `HdlcFrameReader`: the abort sequence is only recognised together with octet stuffing. `use_abort_sequence=True` without `use_octet_stuffing` has no effect and gives a `UserWarning` ([#15](https://github.com/toreamun/amshan/pull/15)).
- `HdlcFrameReader`: a broken frame that ends exactly at its length is returned as invalid, and its octets are then read again, so the same octets can give one invalid and one valid frame ([#16](https://github.com/toreamun/amshan/pull/16)).
- Packaging with `pyproject.toml`, CI with ruff and mypy, and publishing with PyPI Trusted Publishing ([#12](https://github.com/toreamun/amshan/pull/12)).
- The package version is taken from the git tag ([#18](https://github.com/toreamun/amshan/pull/18)).

### Tests

- Test coverage raised to about 99 %, with property-based tests (Hypothesis) and a corpus of public meter messages ([#14](https://github.com/toreamun/amshan/pull/14)).

## 2.1.1 and earlier

See the [GitHub releases](https://github.com/toreamun/amshan/releases).
