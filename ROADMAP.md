# rpi-sdinfo roadmap

Status of the Python tool and what's left before a v1.0.
The bash original (`archive/rpi-sdinfo.sh`) is kept for reference only and is not being developed further.

## Done in 0.3

- Fixed crash bugs in the old fio result loop (per-run `IndexError`, `--max-jobs` str+int concat).
- `read_file()` returns `''` (not `None`) for a missing file, so a Pi Zero with no `eth0` no longer crashes.
- Filesystem (`dumpe2fs`) and memory (`/proc/meminfo`) parsed by attribute label via `parse_kv()`, not by
  fragile line number / character offset.
- Disk-throughput maths guarded against divide-by-zero (`safe_div`); device `uuid` salt fixed so the
  anonymised identifier is stable across runs.
- **Core feature implemented**: grade measured performance (median of the best half of runs) against the card's
  rated speed class, falling back to A1. PASS/FAIL per metric, overall result, non-zero exit on failure.

## Done in 0.4

- **Native benchmark — fio dependency removed.** New `sdbench.py` is a dependency-free, pure-stdlib benchmark
  (sequential write, random 4 KiB read/write IOPS + latency) that runs on Linux and macOS. Cache-bypassing via
  F_NOCACHE (macOS) and O_DSYNC + `posix_fadvise(DONTNEED)` (Linux). Usable standalone (`python3 sdbench.py`) or
  imported by `rpi-sdinfo`. Hardware-independent parts tested on macOS.
- **Cross-platform.** `rpi-sdinfo.py` now runs on macOS as well as Raspberry Pi Linux:
  - Linux: unchanged full detail (CID/CSD registers, filesystem, IO stats).
  - macOS: identity via `diskutil` (capacity, media name, bus, SMART, removable). macOS cannot expose the SD
    CID/CSD registers, so make/model/speed-class are unknown there and grading falls back to A1. Benchmark and
    grading work on both.
- **Restructured** from a top-level script into functions with a `main()` / `if __name__ == '__main__'` guard,
  `argparse` (`--device`, `--partition`, `--dir`, `--runs`, `--size-mb`, `--seconds`, `--no-benchmark`), and the
  `apt` import removed. Shebang fixed to `env python3`.
- **`SD_CARDS.md`** reference added (CID fields, label symbols, class→performance tables, Pi bus ceilings,
  counterfeit tells).

## Done in 0.5

- **New CLI experience.** A shared, dependency-free `ui.py` renders a colourful, sectioned report (banner,
  key/value rows, PASS/FAIL badges, proportion bars, a rounded verdict box) with a live progress spinner during
  the benchmark. Colour auto-detects a TTY and honours `NO_COLOR` / `CLICOLOR_FORCE`, with `--color` / `--no-color`
  overrides and an ASCII fallback for non-UTF terminals.
- **Machine-readable output.** `--format json` (alias `--json`) emits the whole result as one JSON document on
  stdout (`schema`, `tool_version`, `generated`, identity, `benchmark` samples, `grade`); all progress/messages
  go to stderr so pipelines stay clean. `--quiet` prints nothing but still sets the exit code. Exit codes
  documented (0 pass / 1 fail / 2 usage). `sdbench.py` gained `--json` too.
- **Windows support.** New `gather_windows()` (capacity, volume label, removable flag via the Win32 API + a
  drive-root `shutil.disk_usage`), on-the-fly ANSI enablement on Windows 10+ consoles, and `sdbench` made
  Windows-safe (portable `pread`/`pwrite`, `O_BINARY`). Not yet run on real Windows hardware.
- **Refactor.** Gather / compute / render are now separated (`compute_perf`, `compute_grade`, `render_*`,
  `build_json`) so the same data drives both the text and JSON output.

## Done in 0.6

- **Capacity-fraud sweep — the headline fake-detection feature.** New `sdverify.py` is a dependency-free,
  pure-stdlib write-then-verify sweep (the f3 / h2testw technique). It fills the card's free space with test
  files whose every block is stamped with a SHAKE-128 pattern keyed by its absolute offset — unique,
  non-compressible data a cheating controller cannot guess, dedupe, or store cheaply — then reads it all back and
  regenerates the expected pattern per offset. A genuine card verifies every byte; a fake returns zeros, garbage,
  or a wrapped earlier block, and the offset of the first mismatch is the card's true usable capacity. Reads
  bypass the OS cache (shared IO helpers with `sdbench`) so a fake can't pass by serving the page cache.
- **Wired into `rpi-sdinfo`** as opt-in `--capacity-check` (with `--capacity-mb` to cap a quick partial sweep and
  `--yes`/confirmation gating, since it fills free space and adds flash wear). A `CAPACITY` report section and a
  `capacity` block in the JSON; a fake now fails the overall exit code. Non-destructive to existing files (its
  own test files are always cleaned up), and a free-space safety margin is always left.
- Verified end-to-end on macOS: genuine cards pass, an injected corruption is caught at the exact byte offset,
  and text / JSON / quiet / confirmation-gate paths all behave.

## Done in 0.7

- **CSD register decode + CID/CSD cross-checks — instant, non-destructive fake detection.** `decode_csd()` parses
  the 128-bit CSD register (v1.0 SDSC / v2.0 SDHC-SDXC / v3.0 SDUC): capacity from the C_SIZE family, max bus
  speed from TRAN_SPEED, command classes, read block length. `cross_check()` then flags internal contradictions,
  the strongest being a **Standard-Capacity (v1.0) CSD on a card that claims more than 2–4 GB** — physically
  impossible per the SD spec, the classic signature of a small card reflashed to lie about its size. Also warns
  on a CSD-vs-reported capacity mismatch and a future CID manufacturing date. A `fail` finding fails the overall
  exit code; a new `CONSISTENCY` report section and a `consistency` block in the JSON. Complements the write-based
  sweep: the sweep proves real size by writing, this catches a liar from its own metadata in milliseconds.
- Decode verified by round-trip encode/decode across all three CSD versions and TRAN_SPEED codes; cross-checks
  verified to fail a reflashed-fake vector and pass a genuine card. No-op (and silent) on macOS / Windows, which
  cannot read the register.

## Done in 0.8

- **`--raw` debug dump.** Captures the verbatim sources behind the friendly report - on Linux the full `dumpe2fs`
  output plus raw `/proc/loadavg`, `/proc/meminfo` and the `/proc/diskstats` line; on macOS the whole `diskutil`
  record; on Windows the Win32 volume query. Rendered as a `RAW` report section (with the decoded CSD fields and
  the raw per-run benchmark samples) and carried as a `raw` block in `--format json`. Off by default so normal
  output and the JSON contract stay clean; the raw block only appears when `--raw` is passed.
- **SQLite persistence.** `--save-db [PATH]` appends the run to a local SQLite database (default
  `~/.rpi-sdinfo/results.db`), creating the file and its directory on first use. One row per run: the full JSON
  document verbatim in a `document` column, plus typed, queryable columns (identity, capacity, measured
  performance, CSD capacity type, and every pass/fail flag) so a history of tested cards - genuine and fake - can
  be queried without parsing JSON in SQL. Local-only, so it keeps the real serial/MACs; a save failure warns but
  never changes the card's exit code. The local seed of the crowd-sourced database below (upload still gated on a
  stronger anonymisation scheme).
- **`--db-query [PATH]` history summary.** Reads the saved database instead of testing a card and prints totals
  (runs, distinct cards, period, pass/fail), a per-card table (grouped by label + CID serial, with run count,
  latest verdict, best sequential write and rated class), and a list of every flagged run with a plain-English
  reason (too slow / capacity fraud / CSD-CID inconsistent). Honours `--json`.
- **Latency percentiles.** `sdbench` now keeps every per-operation latency and reports the distribution
  (mean, p50/p95/p99, min/max in ms) per phase, not just the mean - the tail is what a worn or fake card exposes.
  Surfaced in `sdbench`'s own text/JSON output, in the run's `benchmark` block (`*_latency_pct`), and in the
  `rpi-sdinfo --raw` dump. Percentile helper avoids `statistics.quantiles` so the 3.6 floor holds.
- Verified end-to-end on macOS: `--raw` text/JSON, the raw block's presence gating, two runs (a graded benchmark
  and a `--no-benchmark` run) persisting clean full/partial rows with numeric columns intact, the latency
  distribution, and `--db-query` text/JSON including the flagged-run list (exercised with an injected fake row).

## Next up (v1.0 blockers)

- **Not yet hardware-tested on a Pi.** The macOS path is exercised end-to-end; the Linux `gather_linux()` path
  is preserved from the working 0.3 logic and compiles, but needs a run on a real Pi 3B and Pi Zero W. Watch:
  - `sdbench` write/read units and whether the F_NOCACHE/O_DSYNC path reports realistic SD numbers on a Pi
    (validate against the old fio results and a known card).
  - `dumpe2fs` / `meminfo` label spellings across Raspberry Pi OS versions.
  - `/proc/diskstats` column count/order for the read/write counters.
- **`erase_size` / block size of 0.** The kernel reports `erase_size` as 0 when a card is not block-addressed;
  capacity maths falls back to 512 but should detect and flag the case explicitly.
- **Tighten exception handling.** Narrow the broad `try/except KeyError` around the manufacturer lookups; report
  unreadable sysfs nodes (permissions, missing hardware — `mac_bt0` needs root) with a clear message, not a
  traceback.

## Fake / counterfeit card detection (the reason the tool exists)

- **Capacity fraud test.** ✅ Shipped in 0.6 (`sdverify.py`, `--capacity-check`) and since extended with a
  raw-device **corners sweep** (`sdverify.py --device`): probes block 0, every power-of-two offset, and the last
  block of the reported capacity. Because a fake truncates the block address at a power-of-two boundary R, block
  0 and block R alias onto one physical cell, so the (0, R) pair is always probed — a guaranteed catch for any
  power-of-two address-truncation fake (the standard kind) in ~log₂(N) probes rather than a full-card write.
  Destructive, so gated behind `--yes` and a mounted-device refusal. Still to refine:
  - **Non-power-of-two wraps** can slip past the corners probes (a fake that wraps at, say, exactly 100 GB with
    no power-of-two structure); the thorough free-space sweep still catches those, so corners is a fast
    first-pass, not a replacement. Could add a few congruence-busting probes for common non-binary sizes.
  - **Wire the corners sweep into `rpi-sdinfo`** (e.g. `--capacity-check --raw --device …`) once it can be tested
    on a real removable card - deliberately not auto-wired yet, since a destructive raw write to the wrong
    device must not ship untested on hardware.
  - Raw-device *full* sweep (not just corners) where we have the device and privileges, so a nearly-full card
    can still be exhaustively tested without needing free space.
- **CID/CSD cross-checks.** ✅ Shipped in 0.7 (`cross_check()`): flags a Standard-Capacity CSD claiming a
  high/extended capacity (impossible), a CSD-vs-reported capacity mismatch, and a future manufacturing date.
  Still to add: MID that never ships the branded make, and a rated speed class the CSD's TRAN_SPEED can't
  support (e.g. an A2/U3 label on a card whose CSD only advertises legacy 25 Mbit/s).
- **Decode the CSD register.** ✅ Shipped in 0.7 (`decode_csd()`): structure version → SDSC/SDHC/SDXC/SDUC,
  capacity, TRAN_SPEED bus speed, command classes, read block length - compared against the branding above.

## Data capture & sharing (the "build a public database" idea)

- **Structured output.** ✅ `--format json` ships in 0.5, ✅ local SQLite persistence (`--save-db`) in 0.8.
- **Raw mode.** ✅ Shipped in 0.8 (`--raw`): dumps the full `dumpe2fs` / register / benchmark detail for debugging.
- **Crowd-sourced upload.** Optional POST to an API / S3 bucket so results (CID, CSD, capacity, measured
  performance, pass/fail) build a shared database of card identifiers and real-world failure rates. Needs a
  stronger anonymisation scheme than the current fixed-salt PBKDF2 over the serial (a public salt over a
  low-entropy serial is brute-forceable) — decide what is safe to share before any upload ships.
- **Grow the CID database.** The MID/OID → product table is crowd-sourced and incomplete; every verified
  `CID → real product + measured performance` mapping makes fake-detection stronger.

## Smaller cleanups

- `sdbench`: optional true O_DIRECT path on Linux (aligned buffers) for the most accurate device-level numbers;
  progressively-larger block sizes. ✅ Latency percentiles (not just the mean) shipped in 0.8.
- macOS: resolve the card's product name more reliably for USB card readers, and auto-detect a removable card
  when `--device`/`--dir` is omitted.
- `read_file(return_scope='lines')` only returns a single line; extend it to a range, and test that the `regex`
  scope returns multiple matching lines.
