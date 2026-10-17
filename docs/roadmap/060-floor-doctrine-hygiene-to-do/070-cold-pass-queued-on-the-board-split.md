- [~] **Cold pass queued — the board split (structural change to this repo's record store).** (claimed 2026-10-17-2005, wt: rpi-board-split-cold) For a non-author
      to take. **Brief written 2026-10-03 1151 UTC**, by a non-author session on Opus 5.5 at Mike's instruction (off-tier,
      disclosed in its provenance), for a fresh Fable session to run:
      [`docs/reviews/2026-10-03-1151-board-split-cold.md`](../../reviews/2026-10-03-1151-board-split-cold.md). Its
      delta also takes in `38016b6`, the same session's pin bump.
    - **Claim taken over 2026-10-17 2005 UTC.** The 1211 claim came from a headless Fable session that hit a
      usage limit before reviewing anything: its worktree `rpi-board-split-cold` was clean at `f4951ed` — no
      commits past `main`, no stash, no branch pushed. Taken over on Mike's explicit instruction (2026-10-18 NZ),
      which is a *current* re-assignment from the principal and overrides a live `[~]` (`CONCURRENCY.md`
      § *Claiming work*); the orphan test — commits stopped — is met as well. The same worktree is reused.
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
