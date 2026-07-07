# Contributing to rpi-sdinfo

Thanks for your interest. This is a small, dependency-free tool with a deliberately
low barrier to hacking on it.

## Ground rules

- **Standard library only.** The tool has zero runtime dependencies and that is a
  feature, not an accident — it must run on a stock Raspberry Pi OS, macOS or Windows
  Python with nothing to `pip install`. Please don't add a runtime dependency; reach
  for the stdlib first.
- **Stay cross-platform.** Code runs on Linux (the full path), macOS and Windows.
  Platform-specific code lives behind a `sys.platform` check and degrades gracefully
  (e.g. macOS cannot read the SD CID/CSD registers, so identity is limited there — that
  is expected, not a bug).
- **Target Python 3.6+.** Avoid features newer than 3.6 (for instance, the benchmark's
  percentile helper is hand-rolled rather than using `statistics.quantiles`).
- **Keep the docs in sync.** A change that alters behaviour should update `README.md`,
  `ROADMAP.md`, the man page (`docs/rpi-sdinfo.1`) and `CHANGELOG.md` in the same commit.
  If you change the CLI surface, the man-page update is not optional.
- **Comments say _why_, not _what_.** Platform quirks, SD-spec reasoning and non-obvious
  constraints earn a comment; restating the code does not. `#!#` marks a TODO (more `#`
  after it = higher priority).
- **Record real decisions.** If you reject a plausible alternative or rest a design on
  evidence, add a short numbered ADR under [`docs/decisions/`](docs/decisions/) — it keeps
  a settled call from being re-litigated (e.g. why a fake is deliberately *not* inferred
  from the CSD TRAN_SPEED field, ADR 0003).

## Development setup

```bash
git clone https://github.com/mike548141/rpi && cd rpi
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"     # the three commands, plus ruff for linting
```

You don't have to install to run it — `PYTHONPATH=src python3 -m rpi_sdinfo --help` works
straight from a clone.

## Running the checks (the way CI does)

```bash
python3 -m unittest discover -s tests          # everything (~3 s, no SD card needed)
cd tests && python3 -m unittest test_csd       # a single module
ruff check .                                   # lint (dev-only; config in pyproject.toml)
```

The suite covers all hardware-independent logic. What it **cannot** cover is the Linux
sysfs / `dumpe2fs` / `diskstats` reads in `gather_linux()` — those need a real Raspberry
Pi. If you have Pi hardware, runs of `sudo rpi-sdinfo --raw` against known-genuine and
known-fake cards are especially valuable (see `ROADMAP.md`).

## Generating the SBOM

`tools/gen_sbom.py` emits a CycloneDX 1.5 Software Bill of Materials (stdlib-only, no
dependency — see [ADR 0005](docs/decisions/0005-sbom-cyclonedx.md)):

```bash
python3 tools/gen_sbom.py                    # to stdout
python3 tools/gen_sbom.py -o sbom.cdx.json   # to a file (attached to releases)
```

Because rpi-sdinfo has zero runtime dependencies, the SBOM's `components` list is empty and
the root depends on nothing — a provably tiny supply-chain surface. The version comes from
the package `__version__`; the rest from `pyproject.toml`. Do **not** commit the generated
JSON — it is a build artifact regenerated on tag.

## Pull requests

1. Branch off `main`.
2. Add or update tests for the behaviour you change; keep the suite green.
3. Update the relevant docs and add a `CHANGELOG.md` entry under `[Unreleased]`.
4. Keep commits focused and their messages descriptive.

## Growing the card database

The CID → real-product table (make / model / speed class) is crowd-sourced and incomplete.
A verified `CID → product + measured performance` mapping is a genuinely useful contribution
and makes the fake-detection stronger for everyone.
