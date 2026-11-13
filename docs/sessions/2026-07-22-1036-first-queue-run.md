# 2026-07-22 — First orchestrated queue run

> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `a11e754`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-22** — **First orchestrated queue run** (Fable orchestrating, three Opus agents in parallel
  worktrees; Mike's ask: maximise plan use, take the small/unblocking/nearly-done work first). Doctrine drift
  read (targeted: CONCURRENCY + AUTONOMY deltas; floor unmoved), pin bumped `2b8da3b`→`9e7e031`; the new
  claim-on-main mechanism was used for real — three items claimed `[~]` on `main` before work, each built on
  its own branch/worktree, merged, claim resolved, branch put away. Landed: **(1) brand-set signal, first
  slice** (`brand_sets()`/`brands_observed()`/`validate_brand_sets()` derived live from the CID table; neutral
  `info` context in `cross_check()`; product *labels* deliberately not mined — prose boundaries would fabricate
  brands; +35 tests). **(2) ADR 0008 crowd-upload anonymisation** (Proposed — Mike's ruling owed on five
  questions). 🔎 Its grounding pass corrected a real misconception: the local PBKDF2 hashes the **Pi host**
  serial, not the card's — the card PSN sits in the local DB in the clear, so an upload payload must be
  purpose-built, never a subset of the local row. **(3) raw-device full sweep** (`rpi-sdverify --device --full`,
  write-all-then-verify-all so wraps corrupt before read-back; O(one block) memory; proof-test where a 33-block
  arbitrary-wrap fake passes corners but is caught by full; +8 tests). File-tested only — hardware validation
  joins the Pi blocker. Known nuance (recorded, not fixed): on a pure-modulo wrap the first mismatch lands at
  offset 0, so `usable_estimate_bytes` reads 0 — honest (the head really is clobbered) but differs from a
  truncating fake, which pins the mismatch at the real boundary. 138→**181 tests green** on `main`; ruff not
  installed locally (CI lints); everything pushed as it landed (per the 2026-07-10 standing grant + concurrency
  doctrine — the old "Mike syncs himself" habit is retired). **Next**: all remaining work is gated — Pi
  hardware (v1.0 blocker; corners/full/O_DIRECT validation), Mike's rulings (ADR 0008's five questions; tag
  `v0.9.1`; PyPI-or-not), or real cards (CID DB growth). The suspicion score stays deliberately deferred until
  the brand table is richer (own ADR when it comes).
