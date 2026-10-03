# Deferred — the brief-writer's observations (board-split cold pass)

**Open this only after your own findings are committed.** It goes with
[`2026-10-03-1151-board-split-cold.md`](2026-10-03-1151-board-split-cold.md)
(REVIEW.md rule 1). These are observations the brief-writer formed while it
was finding the work. They are framing, not findings: each one is a claim for
you to test, and none of them limits what you look at. When the verdict lands,
fold this file into the brief below the verdict and delete it.

1. **Atelier records this repo as "born split".** The fleet-rollout item
   (`../atelier/docs/roadmap/010-board-store-migration-per-item-files-mik/030-fleet-rollout-of-the-split-board.md`)
   lists this repo's index as "— → 69, born split, no prior `ROADMAP.md`". It
   argues from that that the store form was adopted "without a monolith to
   convert". Commit `4bd429c` deletes a 245-line *root* `ROADMAP.md`. The
   item's method counted `docs/ROADMAP.md`. Whether this is a harvest finding
   against this delta, or atelier's alone, is your call. Correcting atelier's
   board is atelier's work, and nobody has asked for it from this repo.
2. **`38016b6` has no review line of its own.** It rewrote the inlined doctrine
   floor, so under REVIEW.md § *Review the design* it owes a queued pointer or an
   explicit `review: not warranted — grounds`. Item `060/010` carries neither.
   The `070` pointer names only the split's commits. The brief folds `38016b6`
   in rather than leaving it unpointed.
3. **The pin is stale, and the tooling does not follow the pin.** At brief time
   atelier was 505 commits past `0af3006` (`git -C ../atelier log --oneline
   0af3006..HEAD | wc -l`, 2026-10-03 1151 UTC). The board generator and the floor
   run from atelier's working tree, so the index this pass regenerates comes
   from tooling that has moved since the split. The brief-writer did not bump
   the pin, because that would have edited `CLAUDE.md` under review mid-pass.
4. **The BS1 residual that `060/060` names may have moved upstream.** At
   landing, atelier's board-store cycle was open on BS1: the hook-plane `board`
   check compared worktree to worktree. Atelier's commit subjects since then
   include `b2a54f1` "floor: wire the staged plane at the hook". So the
   residual the item states may no longer hold as written.
