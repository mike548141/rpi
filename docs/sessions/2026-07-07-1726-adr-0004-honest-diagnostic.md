# 2026-07-08 (cont. 3) — ADR 0004: an honest diagnostic, not a pass/fail toy

> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `1b2cbfe`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-08 (cont. 3)**: Also captured the **product-philosophy** point as **ADR 0004** ("honest diagnostic,
  not a pass/fail toy" — the tool diagnoses genuine-but-faulty / worn / honestly-slow / bus-bottlenecked cards,
  not just fakes, for a capable audience; ADR 0003 is its worked example), threaded into the README scope and a
  CLAUDE.md design principle, plus a project memory. Then knocked off the **`read_file` line-range** cleanup:
  the `lines` scope now takes an int (single line), a `(start, stop[, step])` tuple or a `slice` (range, joined),
  or nothing (whole file); an out-of-range int degrades to `''` (a slice just clamps). No caller uses the `lines`
  scope yet, so backward-compat risk is nil. The roadmap's paired ask — that `regex` returns multiple lines — was
  already covered by an existing test; added 6 new `lines` tests. 102 tests green; `py_compile` clean. Docs
  synced (ROADMAP ✅, CHANGELOG). Commits: `d3542ac` (ADR 0004), + this read_file commit. **Next**: the standing
  v1.0 Pi-hardware blocker is the only big rock left that's testable *only* on hardware; the release track
  (v0.9.0 tag / PyPI / SBOM) needs Mike's go-ahead and the anonymisation decision. Bench of small cleanups is
  now essentially drained.
