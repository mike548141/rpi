# Sibling to the floor-restamp-0a2b7a7 cold pass — held under rule 1's split

Sibling of `docs/reviews/2026-11-01-1202-floor-restamp-0a2b7a7-cold.md`, held under
atelier `docs/method/REVIEW.md` rule 1's split. **Open only after the phase-1
findings in the brief are committed.** Written 2026-11-01 UTC by the Opus 5.5
brief-writer named in the brief's provenance; it forms no finding and writes no
severity. Fold this file in below the reconcile and delete it.

## Re-run results held back from the brief

Run once by the brief-writer, 2026-11-01 UTC, from a worktree at `102e909` outside
the sibling layout, atelier tools at `7bd98ce`, machine load near 13.

1. Canonical region at `0a2b7a7`: 95 lines, including an opening and a closing
   code-fence line. Placeholder tokens: `<SHA>` ×2, `<atelier-path>` ×3, `<visibility
   fact>` ×1, `<owner/repo>` ×1 (four distinct placeholders, seven occurrences).
2. `diff canon copy` at HEAD: exit 1, three hunks (22 diff lines): the fence lines
   plus the heading's `<SHA>`; the three *Source & drift* lines; the visibility
   bullet. The stamped block at `f56c5d5` and at HEAD are identical.
3. The visibility fill is three lines: the status with a date, a reason that links an
   ADR, then the verify line.
4. `git log f56c5d5..HEAD -- CLAUDE.md`: one commit, `cd41c64`.
5. CI-plane floor on this machine: **exit 1, blocked by `leakscan`** (11 `local-term`
   findings, from the machine-local term list, across `archive/`, `docs/SESSIONS.md`,
   ADR 0009 and the man page, among others); `secretscan` clean with 30 advisories.
   The machine-local term list does not exist on a GitHub runner, so the pushed CI
   run is a different measurement; not checked.
6. Board check: exit 0.

## Brief-writer's questions, for reconcile

1. R2 says "three placeholder fills"; the *Beneath the floor* preamble and
   `CHANGELOG.md` say "the four placeholders". Which count is the record's, and does
   either match the seven occurrences?
2. The visibility fill carries a markdown link to an ADR. Is a link a fact, and does
   a reader of the floor alone (atelier unread) need the target to exist?
3. The drift check as stamped fails from a worktree outside the sibling layout
   (`../atelier` does not resolve), while the floor tells sessions to take worktrees.
   A finding on the copy, the canonical, or a hand-up?
4. `cd41c64` adds a standing rule beneath the floor and calls the change "recording
   two principal rulings". Is adopting a general rule into standing text a record or
   doctrine, and does rule 4 bind it?
5. `cd41c64` also replaces a board-check note with a pointer to atelier's
   `CONCURRENCY.md` § *On a split board*. Does that section say what the removed note
   said, at the pin?
6. R3's "publication" warning moved beneath the block. The floor's own visibility
   bullet now carries less than the repo's local rule says. Does a session that reads
   only the block still learn that a push here is publication?
7. `102e909` exempts `docs/SESSIONS.md` and `CHANGELOG.md` whole from wrapscan,
   though new entries are appended to both; the ruling it applies was "85 for new,
   exempt history". Does the exemption match the ruling for new entries? (Out of the
   pointer's delta; raised because it is the same session-close surface.)
8. The CI-plane floor on this machine blocks on `leakscan` local-term findings at
   HEAD. Did the delta's own landing pass the hook plane, and is the close's "pushed
   floor run" rule (beneath the floor) met by the record?
9. R6 notes the cheapest-model ruling widens `060/050`'s conflict. Was that conflict,
   a contradiction between this repo's docs and house doctrine, carried as a finding
   to be fixed or as a note?
