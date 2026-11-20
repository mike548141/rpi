# 2026-07-29 (cont.) — CI red to green, then the flip to public

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 36+1 -->
- [2026-07-29 (cont.) · CI red to green, then the flip to public](2026-07-29-1129-ci-green-then-public.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `e7872d5`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Its 1 relative link moved one directory up (`../`); nothing else changed.

- **2026-07-29 (cont.)** — **CI red → green, then the flip.** Mike ruled on both open questions from the
  publish-safety review: fix CI *now*, then go public. He also set a standing policy worth recording —
  **Linux + macOS are tier 1, Windows tier 2** ([ADR 0010](../decisions/0010-platform-support-tiers.md)) — which is
  what decided *how* to fix, not just whether. 🔎 The Windows red was two different things, and only the tier
  ruling separates them: **(1) a genuine product bug** — `_device_io()` in `verify.py` called `os.pwrite`
  directly (POSIX-only), so the whole raw-device sweep died with `AttributeError` on Windows, while the sibling
  `pread` in the *same function* already went through `bench.py`'s portable shim. An oversight, not a considered
  limit. **(2) a test-harness defect** — `os.geteuid()` evaluated inside a `@skipIf` decorator, i.e. at import
  time, taking the whole `test_helpers` module down. Both fixed. The regression test pins the **routing**
  (`sdbench._pwrite` is called) rather than the platform, so it fails on macOS/Linux if the shim is ever bypassed
  again — a Windows-only test would never have run where the bug was actually introduced. Fixing the import
  crash then surfaced a third failure it had been *masking*: `test_unreadable_returns_empty_not_traceback`
  chmods a file to 0o000 and expects `read_file` to degrade to `''`, but Windows `chmod` only toggles the
  read-only flag, so the file stayed readable. Not a product bug — a precondition the platform cannot establish.
  Fixed by making the test **verify its own precondition** (try the read, skip if it succeeds) rather than
  hardcoding a `sys.platform` skip: it stays live wherever the condition holds, including as root. Also cleared the two
  `E402`s a newer `ruff` began enforcing (`# noqa: E402` — both imports sit deliberately beside the comment that
  explains them). 182 tests green, ruff clean, CI green on all three OSes. Tier policy recorded in ADR 0010 +
  README + CLAUDE.md so it constrains future platform work instead of being rediscovered from a red run.
  🚀 **Then flipped `rpi` to PUBLIC** on Mike's explicit instruction — the always-stop-and-confirm floor action,
  authorised in writing, not originated here. **Next**: `ros` and `faves` against this now-proven checklist
  (noting `ros`'s 537,748 leakscan reds are almost certainly a scoping fault, which must be *proven* before it
  goes anywhere); the standing v1.0 Pi-hardware blocker is untouched by any of this.
