# 2026-11-13 0608 UTC — pin bump to `2a6d7a4`, CI back to green

A headless Opus 5.5 session, dispatched by an estate health sweep (orchestrator
session `e820bff5`), in a detached worktree at `origin/main`. Its brief: the
latest atelier pin, CI green, conformance with the house's current expectations,
and a report of what needs the principal.

## What was done

- ✅ **Pin `0a2b7a7` → `2a6d7a4`** (340 atelier commits). Read in full: the
  `PROPAGATION.md` diff over the range, which holds the `floor` region. The rest
  of the `docs/method` and template delta came from a digest written by a
  read-only research session that read every hunk; it was not re-read here. The
  floor is re-stamped word for word with the same four fills. `pins.py --child`
  reads `current` and `✓ identical`. Detail on [`060/010`](../roadmap/060-floor-doctrine-hygiene-to-do/010-bump-the-atelier-pin.md).
- ✅ **Read order:** the session-log step gains the cold-reviewer clause
  (`REVIEW.md` rule 2).
- ✅ **CI fixed** (`070/040`): `ubuntu-latest` is now 26.04, with no 3.8 or 3.9
  build in `setup-python`. Those two Linux entries moved to `ubuntu-22.04`; the
  declared Python floor is unchanged. `CI` and `floor` green at `013f41b`.
- ✅ **FS3 of `060/100` applied** (records route): eleven author-byline
  `leakscan` markers scoped to `local-term` (three also to `nz-address`). The
  whole-tree floor is now green on a machine with the term list.

## Checked and left alone

- No `Pending upstream:` lines exist. No exemption in this repo departs from a
  rule the delta moved (CF3, E6d(i), estate-root naming, asking).
- Dated gates: no tracked binaries (the 2026-11-18 leakscan gate has nothing to
  hold); the board index is current; no sizescan advisory or disabled entry.
- `allowmarker --census` reports one malformed marker, in
  `docs/reviews/2026-10-03-1151-board-split-cold.md` line 460. It is a quoted
  marker in a review's counsel that wraps across a line, not a live exemption,
  so losing it on 2026-12-09 exempts nothing that needs exempting. Left as is.
- The session log is still a flat log of long entries. This entry starts the
  index-plus-detail form; rotating older entries to an archive was not done.
- No cold pass is queued for this re-stamp. Whether a verbatim re-stamp that a
  tool has verified still earns a Fable pass is the principal's call, and it is
  in the sweep's report.

## Identifiers

- Commits: `013f41b` (bump, CI fix, FS3) and this entry's landing commit.
- Board: `060/010` (bump recorded), `060/100` (FS3 noted), `070/040` closed.
- Runs at `013f41b`: [CI 43378313548](https://github.com/mike548141/rpi/actions/runs/43378313548),
  [floor 43378313900](https://github.com/mike548141/rpi/actions/runs/43378313900).
- No PRs, no agents, no other repos written.
