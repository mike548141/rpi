# 0010 — Platform support tiers: Linux and macOS tier 1, Windows tier 2

**Status**: accepted • **Date**: 2026-07-29

## Context

The tool has always claimed three platforms, and the CI matrix has always run all three
(Linux, macOS, Windows × Python 3.8–3.13). What was never written down is whether they are
*equal* — and the absence of that ruling had a cost.

Windows CI had been failing on every run. Two distinct causes, and the difference between
them is exactly what a tier policy exists to settle:

- **A genuine product bug.** `_device_io()` in `verify.py` called `os.pwrite` directly. That
  call is POSIX-only, so the entire raw-device sweep died with `AttributeError` on Windows.
  The sibling line in the same function already routed through `bench.py`'s portable
  `_pwrite` shim — so this was an oversight, not a considered platform limit.
- **A test-harness defect.** `tests/test_helpers.py` evaluated `os.geteuid()` inside a
  `@skipIf` decorator, which runs at import time. POSIX-only again, so the whole module
  failed to import on Windows.

Neither was a decision anyone made. Both survived because nothing said what Windows was
*owed*.

## Decision

**Linux and macOS are tier 1. Windows is tier 2.** (Owner's ruling, 2026-07-29.)

- **Tier 1 — Linux, macOS.** The primary targets. A platform bug here is a release blocker.
  Raspberry Pi Linux remains the fullest experience, as it is the only platform exposing the
  SD CID/CSD registers.
- **Tier 2 — Windows.** Supported and CI-tested on every push, and expected to **degrade**,
  never to crash. A missing capability that reports itself honestly is acceptable; an
  `AttributeError` from an unguarded syscall is a bug at any tier.
- **All three OSes stay in the CI matrix.** Tier 2 is a statement about the *feature bar*,
  not about test coverage — a tier that is not exercised is a tier that quietly rots, which
  is precisely how the two defects above survived.

**The engineering rule this implies:** a POSIX-only syscall is never called bare. It goes
behind a `hasattr` shim with a fallback — `bench.py`'s `_pread`/`_pwrite` pair is the
pattern to copy, and the existing `fcntl`, `O_DSYNC`, `O_DIRECT` and `posix_fadvise` guards
are the same idea. This applies to test code as much as to product code.

## Rejected

- **Dropping Windows from the CI matrix** to make the red go away. Rejected outright: it
  would convert a *visible* defect into a silent one. The CI spend is US$0.52/month and goes
  to zero on a public repo, so there is nothing to save.
- **Dropping Windows support entirely.** Rejected: the identity/benchmark/grading path works
  there, and a counterfeit card is at least as likely to be checked from a Windows desktop as
  from a Pi. The audience is wider than the development environment.
- **Promoting Windows to tier 1.** Rejected: it cannot read the CID/CSD registers, so the
  counterfeit-detection story is structurally weaker there, and the maintainer does not run
  Windows. Claiming parity would be a promise the project cannot keep — and this repo does
  not make claims stronger than its evidence (ADR 0004).

## Consequences

- Both defects are fixed, and Windows CI is green.
- The `os.pwrite` fix is covered by a regression test that pins the *routing* rather than the
  platform (`test_device_io_writes_through_the_portable_shim`), so it fails on Linux/macOS if
  the shim is ever bypassed again — a Windows-only test would never have run where the bug
  was introduced.
- The tier policy is stated in README and CLAUDE.md, so it constrains future platform work
  instead of having to be rediscovered from a red CI run.
- **Unchanged:** the Raspberry Pi hardware path remains the standing v1.0 blocker. Tiering
  says nothing about it — that gap is about the absence of hardware, not about platform rank.
