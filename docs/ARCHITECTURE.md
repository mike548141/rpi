# rpi-sdinfo architecture

How the tool is put together and why. Design decisions with a rejected alternative live as ADRs under
[`decisions/`](decisions/); this file is the map. Keep it current when the shape changes.

## What it is

A zero-dependency, cross-platform CLI that identifies, benchmarks and — the reason it exists —
**fake-checks** SD/MMC cards. Everything else supports counterfeit detection. Standard library only, Python
3.6+ (ADR [0001](decisions/0001-stdlib-only-zero-runtime-deps.md)).

## Package layout (`src/rpi_sdinfo/`)

| Module | Responsibility |
|--------|----------------|
| `cli.py` | The `rpi-sdinfo` command: gather → compute → render/emit, plus CSD decode, cross-checks, and SQLite history. The orchestrator. |
| `bench.py` | The `rpi-sdbench` command and the reusable benchmark: sequential write + random 4 KiB read/write IOPS and latency, with cache-bypassing IO. Usable standalone or imported by `cli`. |
| `verify.py` | The `rpi-sdverify` command and the write-then-verify capacity sweep (the f3 / h2testw technique) plus the raw-device corners sweep. |
| `ui.py` | Shared, dependency-free rendering: `Console` (banner, key/value rows, PASS/FAIL badges, bars, verdict box), `Spinner`, colour/ANSI capability detection. No domain logic. |
| `__main__.py` | `python -m rpi_sdinfo` entry point. |

`bench.py` and `verify.py` share the cache-bypassing IO helpers so a fake cannot pass by serving the OS page
cache. Three console scripts map to `cli:main`, `bench:main`, `verify:main` (see `pyproject.toml`).

## The pipeline

One run flows through four stages, kept separate so the same data drives both the text report and the JSON:

1. **Gather** — `gather()` dispatches on `sys.platform` to `gather_linux()`, `gather_macos()` or
   `gather_windows()`, each returning a `sys_info` dict with a common `storage`/`hardware`/`software` shape.
   This is the only platform-specific layer.
2. **Compute** — pure functions derive results onto `sys_info`: `compute_perf()` (benchmark), `compute_grade()`
   (measured vs rated class), `compute_consistency()` (`decode_csd()` + `cross_check()`), `compute_capacity()`
   (the opt-in sweep). No I/O beyond the benchmark/sweep themselves; no rendering.
3. **Render / emit** — text mode: `render_report()` + `render_*()` draw sections via `ui.Console`. JSON mode:
   `build_json()` assembles a stable-key-order document (the machine-readable contract). `--quiet` emits nothing
   but still sets the exit code. All progress/messages go to stderr so `--format json` stays pipe-clean.
4. **Persist (optional)** — `--save-db` appends one row per run to a local SQLite DB: the full JSON verbatim in
   a `document` column plus typed, queryable columns (`DB_COLUMNS`). `--db-query` reads it back instead of
   testing a card.

The **exit code** is the verdict: 0 pass, 1 fail (too slow / capacity fraud / an impossible CSD/CID
self-declaration), 2 usage.

## The two fake-detection strategies (complementary, by design)

1. **Write-and-verify (proof by writing)** — `verify.py`. Fills space with offset-keyed SHAKE-128 patterns a
   cheating controller can't guess/dedupe, reads it back, and the first mismatch offset is the card's true
   usable size. The raw-device **corners sweep** probes block 0, every power-of-two offset and the last block;
   because a power-of-two address-truncation fake aliases block 0 onto block R, the `(0, R)` pair is a
   guaranteed catch in ~log₂(N) probes. Destructive on `--device`; gated behind `--yes` + a mounted refusal.
2. **Metadata contradiction (proof by lying)** — `cli.py` `cross_check()` on the decoded CSD/CID. Catches a
   Standard-Capacity CSD claiming high/extended capacity (impossible), CSD-vs-reported capacity mismatch, a
   future manufacturing date, and a **structurally malformed register** (reserved structure version,
   zero/undefined TRAN_SPEED, empty/mandatory-missing command classes, illegal READ_BL_LEN). Instant and
   non-destructive.

The sweep proves real size by writing; the metadata check catches a liar from its own registers in
milliseconds. What we deliberately do **not** do is infer a fake from TRAN_SPEED-vs-class — see ADR
[0003](decisions/0003-tran-speed-is-not-proof-of-fake.md).

## Platform degradation model

Linux (Raspberry Pi) is the full path: it alone can read the SD **CID/CSD registers** from sysfs, so make /
model / rated class / the metadata liar-checks only exist there. macOS and Windows cannot expose those
registers — identity is limited to capacity / label / bus / removable (via `diskutil` / the Win32 API), and
grading falls back to A1. **This is expected, not a bug.** Benchmark, capacity sweep and grading work
everywhere. Platform code sits behind `sys.platform`; a capability the OS doesn't offer degrades to a blank
field or a silent no-op, never a crash.

## Testing

`tests/` is stdlib `unittest`, no dependencies, ~3 s, green on Linux/macOS/Windows (`_loader.py` puts `src/` on
the path). It pins the **hardware-independent** logic: CSD decode round-trips, `cross_check()` fake/genuine
vectors, capacity/grade maths, latency percentiles, the offset-keyed sweep pattern (incl. a simulated
power-of-two fake proving the `(0, R)` alias is always caught), the macOS identity helpers, and an end-to-end
CLI smoke test driving the real write/verify paths against a scratch file.

What tests **cannot** cover is the Linux sysfs / `dumpe2fs` / `diskstats` reads in `gather_linux()` and whether
the cache-bypassing benchmark reports realistic numbers on a real Pi — that needs hardware and is the standing
v1.0 blocker (see [`../ROADMAP.md`](../ROADMAP.md)). Don't claim the Linux path is verified.

## Conventions

Comments explain *why* / platform quirks / non-obvious constraints, not *what* the code does. `#!#` marks a TODO
(more `#` = higher priority). A behaviour change updates its test and the docs (README, ROADMAP,
`docs/rpi-sdinfo.1`, CHANGELOG) in the same commit. `ruff check .` is clean (dev-only; config in
`pyproject.toml`). A decision that rejects a plausible alternative earns an ADR.
