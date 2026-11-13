# 2026-07-30 (cont.) — Flaky CI test pinned and fixed

> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `15589f6`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-30 (cont.)** — **Flaky CI test pinned and fixed.** Verifying the push above went green caught CI
  red on `test_block_sweep_in_benchmark_block` (ubuntu py3.11 + py3.13) — pre-existing flake, nothing to do
  with the docs-only change. 🔎 Root cause: with no card class known `sdinfo` grades the medium against the A1
  floor (ADR 0004 — honest grading), and a shared CI runner's ephemeral disk under O_DSYNC genuinely dips
  below A1 sometimes (the two failed jobs measured 8.3 MBps seq / 54 write IOPS — both below the 10 MBps /
  500 IOPS A1 targets). The tool behaved as designed; the *test* wrongly assumed the runner's disk always
  grades a pass. Fix: the test now accepts exit 0 or 1 (graded-slow is a legitimate verdict; exit 2 still
  fails) — its contract is the JSON shape, not CI disk speed. `sdbench`'s own CLI tests are not exposed (it
  measures, never grades, always exits 0 in JSON mode). 182 tests green locally.
