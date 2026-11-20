# 2026-07-09 — Queue build: `--block-sweep` shipped

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 31+1 -->
- [2026-07-09 · Queue build: `--block-sweep` shipped](2026-07-08-1334-block-size-sweep.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `c7629fb`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-09**: Mike asked me to build from the queue until it made sense to stop and save money. The one
  clearly buildable-*and*-testable-here item left was the roadmap's "progressively-larger block sizes" cleanup —
  shipped it as **`--block-sweep`**. `bench.py`: `SWEEP_BLOCKS` (4 KiB→1 MiB), a pure `_sweep_blocks()`
  (clamps each block to the file size and de-dups, so a small file collapses redundant passes), `_fmt_block()`
  (MiB/KiB label), and `block_size_sweep()` reusing `sequential_write()` at each block — one non-destructive
  pass per size over the existing test file. Opt-in flag on **both** entry points: standalone `rpi-sdbench`
  (top-level JSON `block_sweep`) and combined `rpi-sdinfo` (JSON `benchmark.block_sweep`, via `compute_perf`
  stashing on `perf` so it rides `doc['benchmark']` for free), each with a "Block-size sweep" text section. The
  curve is the honest-diagnostic payoff: a genuine card climbs then plateaus past its page/erase granularity, so
  a flat/collapsing/non-scaling curve is a worn-or-fake tell (not a pass/fail). Verified end-to-end on macOS
  (text + JSON, both tools; confirmed absent without the flag) — the measured curve rises 4→64 KiB then plateaus
  as expected. Added 9 tests (2 pure `_sweep_blocks`/`_fmt_block` classes + real-IO sweep + two CLI smoke tests);
  **118 green**, `py_compile` clean; ruff still not installed locally (CI lints). Docs synced: ROADMAP cleanup
  ✅ (O_DIRECT half still needs a Pi), CHANGELOG `[Unreleased]`/Added, man page `--block-sweep`, README example +
  options. Commits `893920d` (bench), `d48ebc3` (cli wiring). **Nothing pushed** — now 13 local commits on `main`
  since last sync (`d5c3c83`→`d48ebc3`). **Next / stopping here to save money**: the testable-here bench is
  genuinely drained again. Everything remaining is hardware-gated (the v1.0 Pi blocker; the non-power-of-two
  arbitrary-wrap raw sweep; the O_DIRECT path) or a Mike decision — tag `v0.9.1`, PyPI-or-not, and the
  crowd-upload **anonymisation scheme** (a real privacy call for a possibly-public tool: what's safe to share,
  and replacing the brute-forceable fixed-salt PBKDF2 over a low-entropy serial). That anonymisation decision is
  the natural next thing to *decide* before more code is worth writing.
