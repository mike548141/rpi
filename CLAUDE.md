# CLAUDE.md — context for AI sessions on this repo

Orientation for any future session. Canonical detail lives in the docs linked below; this file is the
map, not a copy. Keep it short and current.

## What this repo is

`rpi-sdinfo` — a zero-dependency, cross-platform (Raspberry Pi Linux / macOS / Windows) CLI that identifies,
benchmarks and **fake-checks** SD/MMC cards. Installable `rpi_sdinfo` package (src layout) exposing three
console scripts: `rpi-sdinfo`, `rpi-sdbench`, `rpi-sdverify`. The reason the tool exists is **counterfeit
detection** (capacity fraud + CID/CSD metadata contradictions); everything else supports that.

- **Scope & expectations** (what it is / is not / honest limitations): see the "Scope & expectations" section
  of [README.md](README.md). Short version: a portable *sanity check*, not a certified benchmark or a
  replacement for `f3`/h2testw/`smartctl` — its edge is breadth in one command plus CSD liar-detection.
- **Status, done/planned, open decisions:** [ROADMAP.md](ROADMAP.md) is the source of truth.
- **History of changes:** [CHANGELOG.md](CHANGELOG.md). **Contributor rules:** [CONTRIBUTING.md](CONTRIBUTING.md).
- **SD card domain knowledge** (CID/CSD, class symbols, fakes): [SD_CARDS.md](SD_CARDS.md).

## Design principles (do not violate without discussing)

- **Standard library only — zero runtime dependencies.** Must run on stock Pi OS / macOS / Windows Python with
  nothing to `pip install`. Reach for the stdlib before shelling out or adding a dep.
- **Cross-platform, degrade gracefully.** Platform code sits behind `sys.platform`. macOS/Windows can't read the
  SD CID/CSD registers — limited identity there is expected, not a bug.
- **Python 3.6+ floor.** Avoid newer features (e.g. the percentile helper is hand-rolled, not
  `statistics.quantiles`).
- **Keep docs in sync in the same change** — README, ROADMAP, `docs/rpi-sdinfo.1`, CHANGELOG.

## Working conventions in this repo

- **Commit as work completes; don't wait to be asked.** History commits directly to `main`. Only *push* when
  asked. Use the repo's message style + the `Co-Authored-By` trailer.
- **Tests:** `python3 -m unittest discover -s tests` (stdlib `unittest`, no deps, ~3 s). Add/adjust tests with
  behaviour changes and keep the suite green. The package must stay importable via `src/` on the path (tests do
  this through `tests/_loader.py`).
- **CI** (`.github/workflows/ci.yml`) runs the suite on Linux/macOS/Windows × Py 3.8–3.13. It does **not**
  exercise the Pi sysfs reads — no SD card in CI.
- **Permissions:** keep `.claude/settings.json`'s Bash allow-list broad and prefer the Read/Grep/Edit tools over
  shell text-munging — the user is strongly averse to permission prompts.

## Key constraint & open threads

- **No Pi hardware in the dev environment.** Development is on macOS, so `gather_linux()` and `sdbench`'s
  Linux IO path **cannot be hardware-tested here** — this is the #1 v1.0 blocker. Flag it; don't claim the Linux
  path is verified.
- **Open decisions (in ROADMAP, the user's call):** the LICENSE-vs-file-header GPL **v2/v3** inconsistency
  (resolve before a public release); converting ~116 functions' `#` lead comments to `"""docstrings"""` for
  documentation-as-code; tagging `v0.9.0` and whether to publish to PyPI.
