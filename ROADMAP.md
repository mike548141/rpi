# rpi-sdinfo roadmap

Status of the Python rewrite (`rpi-sdinfo.py`) and what's left before a v1.0.
The bash original (`rpi-sdinfo.sh`) is kept for reference only and is not being developed further.

## Done in 0.3

- Fixed the fio result loop: dispatch jobs by name, and report each run from the value just appended (was an
  `IndexError` on the first run because the per-run lists were indexed with `run`, which starts at 1).
- Fixed `--max-jobs` being built by concatenating a string with an int.
- `read_file()` now returns `''` (not `None`) for a missing file, so a Pi Zero with no `eth0` no longer crashes;
  missing MACs print as `n/a`.
- Filesystem (`dumpe2fs`) and memory (`/proc/meminfo`) values are now looked up by attribute label via
  `parse_kv()` instead of by hard-coded line number / character offset.
- Disk-throughput maths guarded against divide-by-zero on a card idle since boot (`safe_div`).
- Device `uuid` salt is now fixed so the anonymised identifier is stable across runs (a random salt made it
  useless for the intended shared database).
- **Implemented the core feature**: grade measured performance (best-guess median of the best half of runs)
  against the card's rated speed class, falling back to A1. Prints PASS/FAIL per metric and an overall result,
  and exits non-zero on failure so the tool is usable in automation.
- `exit()` → `sys.exit()`.

## Next up (v1.0 blockers)

- **Not yet hardware-tested.** All 0.3 changes are logic-verified on desktop but the script needs a run on a
  real Pi (a Pi 3B and a Pi Zero W, per the header) before tagging v1.0. Watch especially:
  - fio JSON field names/units (`bw` is KB vs KiB — see "fio units" below).
  - `dumpe2fs` / `meminfo` label spellings across Raspberry Pi OS versions.
- **fio units.** Confirm whether fio reports `bw` in KB or KiB and whether the `/ 1000` scaling to MBps is
  right; label outputs accordingly. (Carried over from the original notes.)
- **`erase_size` / block size of 0.** The kernel reports `erase_size` as 0 when a card is not block-addressed;
  capacity maths currently assumes it equals the block size. Handle the 0 case (fall back to a sane block size
  and flag it).
- **Improve exception handling.** Broad `try/except KeyError` around the manufacturer lookups hides real errors;
  narrow them and report unreadable sysfs nodes (permissions, missing hardware) with a clear message rather than
  a traceback. `mac_bt0` in particular needs root to read debugfs.

## Fake / counterfeit card detection (the reason the tool exists)

- **Capacity fraud test.** The classic counterfeit is a small card reporting a huge capacity. Add an optional
  destructive-safe write-then-verify sweep across the reported capacity (à la f3/h2testw) to prove the card
  actually holds what it claims. Must be clearly opt-in and warn about wear.
- **CID/CSD cross-checks.** Flag cards whose CID branding, declared capacity, and rated speed class are mutually
  inconsistent (e.g. a "SanDisk" MID with an OID that never ships SanDisk, or an A2 label that can't hit A1).
- **Decode the CSD register** (started in the bash version, commented out): structure version → SDSC/SDHC/SDXC,
  supported command classes, and rated bus/write-speed factors, to compare against branding.

## Data capture & sharing (the "build a public database" idea)

- **Structured output.** Add `--json` to emit the whole `sys_info` dict, and optionally persist to a local
  SQLite DB, instead of only pretty-printing.
- **Raw mode.** `--raw` to dump the full `dumpe2fs`/register/`fio` detail for debugging.
- **Crowd-sourced upload.** Optional POST to an API / S3 bucket so results (CID, CSD, capacity, measured
  performance, pass/fail) build a shared database of card identifiers and real-world failure rates. Needs a
  stronger anonymisation scheme than the current fixed-salt PBKDF2 over the serial (a public salt over a
  low-entropy serial is brute-forceable) — decide what is safe to share before any upload ships.

## Smaller cleanups

- `read_file(return_scope='lines')` only returns a single line; extend it to accept a range of line numbers, and
  add a test that the `regex` scope can return multiple matching lines.
- Wrap the top-level script body in `main()` / functions with an `if __name__ == '__main__'` guard so pieces are
  importable and testable (currently everything runs at import time, which also blocks unit testing off-Pi).
- Add `argparse` for `--runs`, `--jobs`, `--device`, and the flags above, replacing the hard-coded constants.
