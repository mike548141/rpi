# rpi-sdinfo roadmap

Status of the Python tool and what's left before a v1.0.
The bash original (`rpi-sdinfo.sh`) is kept for reference only and is not being developed further.

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

- **Capacity fraud test.** The classic counterfeit is a small card reporting a huge capacity. Add an optional
  write-then-verify sweep across the full reported capacity (à la f3/h2testw), in pure Python so it works on
  both platforms. Must be clearly opt-in and warn about wear/time. This is the single highest-value feature left.
- **CID/CSD cross-checks.** Flag cards whose CID branding, declared capacity, and rated speed class are mutually
  inconsistent (e.g. a MID that never ships the branded make, an A2 label that can't hit A1, a future MDT).
- **Decode the CSD register** (stubbed in the bash version): structure version → SDSC/SDHC/SDXC, command
  classes, rated bus/write-speed factors, to compare against the branding.

## Data capture & sharing (the "build a public database" idea)

- **Structured output.** ✅ `--format json` ships in 0.5. Still to do: optional persist to a local SQLite DB.
- **Raw mode.** `--raw` to dump the full `dumpe2fs` / register / benchmark detail for debugging.
- **Crowd-sourced upload.** Optional POST to an API / S3 bucket so results (CID, CSD, capacity, measured
  performance, pass/fail) build a shared database of card identifiers and real-world failure rates. Needs a
  stronger anonymisation scheme than the current fixed-salt PBKDF2 over the serial (a public salt over a
  low-entropy serial is brute-forceable) — decide what is safe to share before any upload ships.
- **Grow the CID database.** The MID/OID → product table is crowd-sourced and incomplete; every verified
  `CID → real product + measured performance` mapping makes fake-detection stronger.

## Smaller cleanups

- `sdbench`: optional true O_DIRECT path on Linux (aligned buffers) for the most accurate device-level numbers;
  progressively-larger block sizes; expose latency percentiles, not just the mean.
- macOS: resolve the card's product name more reliably for USB card readers, and auto-detect a removable card
  when `--device`/`--dir` is omitted.
- `read_file(return_scope='lines')` only returns a single line; extend it to a range, and test that the `regex`
  scope returns multiple matching lines.
