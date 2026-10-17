- [x] **Cold pass run — the board split (structural change to this repo's record store).** ✅ Verdict landed
      2026-10-17 2113 UTC: **PASS-WITH-FINDINGS, 0 MAJOR, 12 MINOR** — cycle closed under the no-MAJOR rule; the
      findings, Mike's five rulings and the two hand-ups are consolidated on
      [`060/090`](090-board-split-cold-pass-follow-ups.md). Taken by a non-author. **Brief written 2026-10-03 1151 UTC**, by a non-author session on Opus 5.5 at Mike's instruction (off-tier,
      disclosed in its provenance), for a fresh Fable session to run:
      [`docs/reviews/2026-10-03-1151-board-split-cold.md`](../../reviews/2026-10-03-1151-board-split-cold.md). Its
      delta also takes in `38016b6`, the same session's pin bump.
    - **Claim taken over 2026-10-17 2005 UTC.** The 1211 claim came from a headless Fable session that hit a
      usage limit before reviewing anything: its worktree `rpi-board-split-cold` was clean at `f4951ed` — no
      commits past `main`, no stash, no branch pushed. Taken over on Mike's explicit instruction (2026-10-18 NZ),
      which is a *current* re-assignment from the principal and overrides a live `[~]` (`CONCURRENCY.md`
      § *Claiming work*); the orphan test — commits stopped — is met as well. The same worktree is reused.
    - **Claim taken over again, 2026-10-17 2050 UTC — the third run.** The 2005 takeover was itself a headless
      Fable run; it died on a credit-balance stop before any verdict landed. The worktree held one uncommitted
      change, the deletion of the `.deferred.md` sibling from the working copy (the phase-1 partition, never
      committed), and nothing else: no commits past `8693a43`, no stash, no verdict text. The sibling was
      restored from git before any reviewer was spawned, so the fresh reviewer starts from a clean tree. Taken
      over on Mike's explicit instruction (2026-10-18 NZ), the same current re-assignment as the 2005 takeover.
      Same worktree, same claim shape as below.
    - **Claim shape (rule-4 disclosure):** taken by a principal-opened, **headless** (`claude -p`, nobody
      watching) cold session on Fable (`claude-fable-5-1`), running reviewer-plus-orchestrator. A fresh Fable
      reviewer subagent, spawned headless by this session, forms every finding and severity with the brief as
      its only framing; this session orchestrates — holds the `.deferred.md` sibling until the findings are
      committed, releases it for the reconcile, and commits the records — and forms no finding and writes no
      severity. Neither seat authored the delta or was started or instructed by its author. ⚠️ **Partition
      limit, stated:** the sibling was committed and published at `0daefff`, so it is reachable from git
      history; the partition is by instruction, by removing the file from the reviewer's working copy for
      phase 1, and by `coldsweep`'s default bar — a strong default with an audit trail, not a structural one.
      The verdict says whether it was opened early. The orchestrator itself read the sibling at session open,
      before any reviewer existed — that is the orchestrator's seat, and it is disclosed here.
    - **Delta:** the commits landing `docs/roadmap/` + `docs/ROADMAP.md`, the deletion of the root `ROADMAP.md`,
      the reference updates in [`CLAUDE.md`](../../../CLAUDE.md), [`README.md`](../../../README.md),
      [`CONTRIBUTING.md`](../../../CONTRIBUTING.md), [`docs/ARCHITECTURE.md`](../../ARCHITECTURE.md) and
      [`docs/MODEL-ECONOMICS.md`](../../MODEL-ECONOMICS.md), and the freeze note on
      [`docs/ROADMAP-DONE.md`](../../ROADMAP-DONE.md).
    - **Intent record:** the session entry in [`docs/SESSIONS.md`](../../SESSIONS.md) for 2026-08-17, and the item
      above.
    - **Governing decision:** atelier's board-store ADR
      (`../atelier/docs/decisions/2026-08-15-0610-board-store-per-item-files.md`), whose own review cycle was open on BS1 when this landed.
    - **Verdict landed 2026-10-17 2113 UTC, by the shape disclosed above.** Phase 1 (findings, provenance, the
      driven checks and re-runs) committed at `3b97b6a` with the sibling absent from the reviewer's working copy
      and, by the reviewer's own statement, never opened from history; the sibling was restored only after that
      commit, and phase 2 (Reconcile, one added finding RB12, the fold, the deletion) landed at `2cf3188`. Record:
      [`docs/reviews/2026-10-03-1151-board-split-cold.md`](../../reviews/2026-10-03-1151-board-split-cold.md).
      The reviewer ran ruff for the first time in this repo's history (clean) and re-drove every recorded proof;
      two did not reproduce (RB2, RB3). Nothing was applied by the pass.
