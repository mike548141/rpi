# Changelog

All notable changes to rpi-sdinfo are recorded here. The format loosely follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/) from v1.0 onward. Dates are ISO-8601.

## [Unreleased]

### Added
- **Signed release artifacts (keyless build provenance).** The release workflow now signs the sdist, wheel and
  SBOM with a GitHub build-provenance attestation (`actions/attest-build-provenance`) - a short-lived
  Sigstore/Fulcio certificate minted from the workflow's OIDC identity (no long-lived key), logged to Rekor,
  carrying a SLSA build-provenance statement. The Sigstore bundle is attached to the Release too, so artifacts
  verify both online (`gh attestation verify <file> --repo mike548141/rpi`) and offline
  (`--bundle rpi-sdinfo.sigstore.jsonl`). Dev/CI-only, no runtime dependency. See
  [ADR 0006](docs/decisions/0006-artifact-signing-build-provenance.md).

## [0.9.1] - 2026-07-08

Post-0.9.0 hardening: stronger fake detection, honest-diagnostic polish, macOS UX, and the release toolchain
(SBOM + a tag-triggered GitHub Release). No breaking changes.

### Added
- **Corners sweep: congruence-busting decimal probes.** The raw-device corners sweep (`sdverify --device`) now
  also probes each common decimal capacity boundary below the reported size (8/16/32/…/512 GB, etc.), not only
  the power-of-two offsets. A counterfeit whose real chip wraps at a round decimal boundary has no power-of-two
  structure, so the old probe set could miss it; probing the boundary itself makes it alias onto block 0 and be
  caught. Still a fast first pass - a truly arbitrary wrap needs the exhaustive free-space sweep.
- **CSD structural liar-checks.** `cross_check()` now flags a CSD register that is structurally malformed - a
  reserved structure version (3), a zero/undefined TRAN_SPEED, empty or missing-mandatory command classes
  (basic/read/write), or an illegal READ_BL_LEN. A genuine controller emits a spec-valid register, so garbage
  here is a counterfeit tell. All `warn` severity (strong hints, not exit-code failures).
- **Bus-ceiling explainer.** When a card's rated class needs more sustained throughput than its CSD's advertised
  bus can carry (e.g. a genuine U3/V30 card on a high-speed ~25 MB/s bus), the tool now emits an `info` note
  explaining that UHS speed is negotiated out-of-band and the card is bus-limited on a non-UHS host - so a real
  card measuring below its label is understood, not mistaken for a fake or silently believed fast. It never
  fails the card: inferring a fake from TRAN_SPEED would false-positive genuine UHS cards.
- **macOS: auto-detect the inserted card.** With no `--device`/`--dir`, `rpi-sdinfo` now scans for a removable
  or external whole disk (preferring an SD-bus reader) and profiles *that* card instead of silently falling back
  to the boot disk, and points the benchmark/sweep at the card's mount point. It announces the selection; pass
  `--device`/`--dir` to override.
- **macOS: real card identity on a built-in SD slot.** Where `diskutil` only sees the reader, the tool now asks
  `system_profiler` (`SPCardReaderDataType`) for the inserted card's own product name, manufacturer and serial,
  filling identity gaps `diskutil` leaves blank. USB card readers still present as generic mass storage.
- **SBOM generator (`tools/gen_sbom.py`).** Emits a CycloneDX 1.5 JSON Software Bill of Materials for the
  package - stdlib-only (no third-party generator), with an empty component list and a no-dependency root that
  makes the zero-runtime-dependency supply chain a machine-readable fact. Dev/release tooling; adds no runtime
  dependency. See ADR 0005.
- **Release workflow (`.github/workflows/release.yml`).** On a `v*` tag it verifies the tag matches
  `__version__`, builds the sdist + wheel, generates the CycloneDX SBOM, and publishes a GitHub Release with all
  three attached (`workflow_dispatch` gives a no-publish dry run). Publishing to PyPI stays intentionally manual.

### Changed
- **`read_file` line-range selection.** The `lines` scope now accepts a range (a `(start, stop[, step])` tuple
  or a `slice`) as well as a single int index, and an out-of-range index degrades to `''` instead of raising -
  consistent with the function's "return '' rather than a traceback" contract. Internal helper; no CLI change.
- **Function docstrings (documentation-as-code).** Every function's leading `#` comment is now a
  `"""docstring"""`, and the public entry points that had none gained a one-liner, so `pydoc`/`help()` and any
  API-doc tool show each function's intent instead of a bare signature. No behaviour change.

## [0.9.0] - 2026-07-06

Packaged for distribution, and the first version with an automated test suite.

### Added
- **Installable package.** Restructured the four flat scripts into a `src/`-layout
  `rpi_sdinfo` package with a `pyproject.toml` (setuptools, zero runtime dependencies)
  and three console entry points: `rpi-sdinfo`, `rpi-sdbench`, `rpi-sdverify`. Also
  runnable as `python -m rpi_sdinfo`. Installs with `pipx install` / `pip install`.
- **Regression test suite** under `tests/` (stdlib `unittest`, 68 tests, no dependencies):
  CSD decode round-trips, `cross_check()` fake/genuine vectors, capacity and grade maths,
  latency percentiles, the offset-keyed sweep pattern and the power-of-two corners-alias
  catch, plus an end-to-end CLI smoke test of the real `sdbench`/`sdverify` write-verify
  paths. Runs on any platform with no SD card required.
- **Man page** (`docs/rpi-sdinfo.1`).
- `resolve_block_size()` detects a card that is not block-addressed (kernel `erase_size` 0)
  and flags the assumed 512-byte block via a `cross_check()` info finding, rather than
  silently trusting the derived capacity.

### Changed
- Version scheme moved to PEP 440 semver (`0.9.0`); previously date-stamped (`0.8-20260705`).
- Replaced the broad `try/except KeyError` blocks around the CID-database lookups with a
  single `_lookup()` helper that also survives a non-dict node (closing a latent `TypeError`).

### Fixed
- `read_file()` now degrades an unreadable / permission-gated node (e.g. the root-only
  Bluetooth identity) to `''` instead of raising, so the tool never tracebacks on it.

## [0.8] - 2026-07-05
- `--raw` debug dump, SQLite persistence (`--save-db`) and `--db-query` history summary,
  and per-phase latency percentiles in the benchmark.

## [0.7] - 2026-07-05
- CSD register decode and CID/CSD cross-checks: metadata-only fake detection.

## [0.6] - 2026-07-05
- Capacity-fraud sweep (`sdverify`, `--capacity-check`) and a raw-device corners sweep.

## [0.5] - 2026-07-05
- New sectioned/colour CLI (`ui`), `--format json`, `--quiet`, and Windows support.

## [0.4] - 2026-07-05
- Native benchmark (`sdbench`) replacing the `fio` dependency; macOS support.

## [0.3] - 2026-07-05
- Crash fixes, robust label-based parsing, and PASS/FAIL speed-class grading.

[Unreleased]: https://github.com/mike548141/rpi/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/mike548141/rpi/releases/tag/v0.9.0
