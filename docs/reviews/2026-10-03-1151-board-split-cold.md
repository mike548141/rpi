# Cold pass — the board split (one file per item, generated index)

**Pass type:** rule-4 cold pass, per atelier `docs/method/REVIEW.md`. The delta
is a structural change to this repo's record store, and part of it is doctrine
by function: the working rules in `CLAUDE.md` and the board legend in
`docs/roadmap/README.md` govern what every later session does at open and close.
The session that landed the delta wrote that text.
**Tier:** Fable (`claude-fable-5-1`, the principal-named review tier, ruling
2026-08-04), **checked at selection by the session that takes this**. A session
not on that tier stops here and takes nothing (REVIEW.md rule 4, stop clause).
**Status:** BRIEF WRITTEN 2026-10-03 1151 UTC (2026-10-04 NZ). Not yet run.
**Queue pointer:**
`docs/roadmap/060-floor-doctrine-hygiene-to-do/070-cold-pass-queued-on-the-board-split.md`.
**Why it earns a review:** every session reads this store at open and writes it
at close. A lossy or wrongly classified conversion fails silently. An item whose
work is still owed can read as done, or a body can fall out of the scanners'
view, and nothing downstream complains. The repo is public, so each push of the
delta was publication.

## Spawn provenance

- **Author of the work under review:** the 2026-08-17 session (commit trailers
  name Claude Opus 5, 1M context) that landed the three commits under *What the
  work is*.
- **Who wrote this brief:** an rpi session Mike opened on 2026-10-04 (NZ) on
  Opus 5.5 (`claude-opus-5-5`). He asked it to find the work that needed briefs
  for a Fable review in a fresh session, and to write them. This session is not
  the author's session, was neither started nor instructed by it, and has
  edited none of the delta's paths.
- ⚠️ **The brief was written off-tier, and this is disclosed rather than
  resolved.** Rule 4 says the non-author who takes the item writes the brief,
  and it checks tier at selection. The principal set this split: Opus writes
  the brief and Fable reviews. The brief-writer formed no finding and assigned
  no severity. Everything this brief says is attackable, including what it says
  the work is, its delta list and its non-goals. The reviewer may widen any of
  them, and should say so in the verdict when it does. Whether an off-tier
  brief-writer is acceptable is Mike's call. It was put to him when this brief
  was handed over.
- **Brief-writer's exposure, disclosed** (material it read before writing): the
  queue pointer; item `060/060` (the work's own account of itself); the tail of
  `docs/SESSIONS.md`, including both 2026-08-17 entries, which are the intent
  record; `38016b6`'s commit message and its `CLAUDE.md` hunk; the `--stat`
  of all three commits; items `060/010`, `060/030`, `060/040` and `060/080`; and,
  as doctrine and template at atelier HEAD, `REVIEW.md`, `skills/review-brief/`,
  a 2026-10-03 atelier cold brief, and atelier's board-store fleet-rollout item.
  It did **not** open `docs/reviews/2026-07-29-1251-post-flip-cold-review.md`
  beyond its file name. Every observation it formed that bears on the delta has
  been moved to the sibling file and kept out of this brief.
- **Who takes the review:** a fresh session Mike opens on the Fable tier. It
  repeats its own provenance in the verdict.
- **Orchestration shape.** The preferred shape is reviewer plus orchestrator,
  if the taking session can spawn a Fable subagent. The session holds the
  `.deferred.md` sibling, the subagent reviews with this brief as its only
  framing, and the sibling is released once the subagent's findings are
  committed. If the session reviews single-seat, the deferral is a default with
  an audit trail and no partition (rule 1). Say in the verdict which shape ran,
  and whether the sibling was opened before the findings were committed.

## What the work is

Diff `eb66c2f..38016b6`. Review the paths at HEAD (`c72a344` or later).

- `4bd429c` (2026-08-17): board: split the roadmap into one file per item, with
  a generated index (50 files)
- `0679384` (2026-08-17): board: correct the item count (29 files, not 28)
- `38016b6` (2026-08-17): doctrine: bump the pin again `2428fdf`→`0af3006`, and
  retrofit the inlined floor. **The queue pointer does not name this commit.**
  The brief-writer added it because it landed in the same session and rewrote
  `CLAUDE.md` doctrine text that `4bd429c` had just written. That widening is
  attackable too.

Delta paths: `docs/roadmap/**`, the generated `docs/ROADMAP.md`, the deleted
root `ROADMAP.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`,
`docs/ARCHITECTURE.md`, `docs/MODEL-ECONOMICS.md`, `docs/ROADMAP-DONE.md` (the
freeze note), `.pathscanignore`, `CHANGELOG.md`, `docs/SESSIONS.md`, and one
comment line each in `src/rpi_sdinfo/bench.py` and `src/rpi_sdinfo/cli.py`.

- **Intent record:** the two 2026-08-17 entries in `docs/SESSIONS.md`; items
  `060/060` and `060/010` (its 2026-08-17 sub-bullet).
- **Governing decision:** atelier's board-store ADR,
  `../atelier/docs/decisions/2026-08-15-0610-board-store-per-item-files.md`,
  with `RECORD.md` § *The roadmap* and `CONCURRENCY.md` § *On a split board*.
- **Machine-local, so no CI review sees it:** the index generator and the
  floor are atelier's tools. They run from a sibling checkout, through
  `git config hooks.atelierTools` at the hook and `../atelier/tools/board.py` as
  the docs cite it. They do not run from the pinned SHA. Establish what CI runs
  in their place from `.github/workflows/floor.yml`.

## Scope

Take the widest scope the work admits: intent, decisions, assumptions, design,
docs, code, tests and live behaviour. The lenses organise it and do not bound
it. **Non-goals**, each itself reviewable:

1. Whether each board item is *right*, for example the Pi-hardware blocker or
   the crowd-upload idea. Only its conversion is in scope.
2. The wrapscan width ruling (item `060/030`, due 2026-10-31). Prose width is
   in scope only where the split changed it.
3. Atelier's `board.py` and board-store ADR *as such*. Their own cycle reviews
   them. Their **application here**, and any way this repo's use departs from
   them, is in scope.

**Drive these, don't read them:**

- **Losslessness.** Take `git show eb66c2f:ROADMAP.md` and compare it, as a
  multiset over every non-heading line, with the item files and section
  `README.md`s at `4bd429c`, allowing for the transformations the work declares.
  Every line you cannot account for is either a declared change or a finding.
- **Classification.** For each migrated item, read the original bullet and
  decide for yourself whether it is `[x]` or `[ ]` *before* you look at what
  the split chose. Then compare.
- **The index.** In a scratch copy, regenerate it at `4bd429c` and at HEAD with
  the board tool, and diff each result against the committed index.
- **The floor, on both planes,** as the hook and CI invoke it. Get the exact
  form from `.githooks/pre-commit` and `.github/workflows/floor.yml`. Then run
  the suite (`python3 -m unittest discover -s tests`) and `ruff check .`.
- **The ritual, from cold.** Follow `CLAUDE.md`'s start-of-session ritual as a
  new session would. Check whether it reaches what it needs, and whether every
  link and path the move repointed resolves.

## The four lenses

1. **Approach & assumptions.** Name the load-bearing assumptions yourself,
   before reading the work's own account of why. Check whether this was the
   right change, made the right way, for this repo.
2. **Correctness & quality.** Check that each declared transformation does what
   it claims. Re-count every figure the records state.
3. **Completeness / harvest.** Find every surface that cites the roadmap's
   location or describes how the board works: in this repo (docs, man page,
   packaging, CI, settings), and in atelier's records of this rollout. Check
   what was missed, and what was duplicated rather than pointed at.
4. **Security & privacy** (mandatory). The repo is public and every push of
   this delta was publication. Check that no estate, personal or private-repo
   detail entered the ~50 rewritten files, including the `CLAUDE.md` doctrine
   block, which cites a sibling repo by relative path. The house scanner
   (`/security-review`) is discharged by grounds. This is a landed delta, and
   it is almost entirely markdown, which the scanner's own exclusions bar. Its
   two `.py` hunks are comment-only. Say so in the verdict, and do the
   design-altitude read by hand.

## Re-run obligation

Each of these claims from the work's records is re-run, not read. A claim
that does not reproduce is a finding.

- The floor ran green on the hook plane. `board` was in scope and enforced, and
  `harvestscan` and `pointerscan` were clean over the split store.
- 182 tests pass.
- `pathscan` returned to its pre-split baseline of 5 findings after the
  `.pathscanignore` entry.
- 7 sections and 29 item files (27 migrated, plus the item and its review
  pointer).
- A purely mechanical split would have produced a board of zero items.
- The inlined floor differs from `PROPAGATION.md`'s canonical block **at
  `0af3006`** in exactly two places.
- ruff was not run at landing. Run it now.

## Landing the verdict

- Append the verdict to this file below a `---` divider. Give findings stable
  IDs, `RB1`, `RB2` and so on. Give each a severity (MAJOR or MINOR) and a
  counselled fix where you can. Close with PASS, PASS-WITH-FINDINGS or FAIL.
- **Sequence:**
  1. Write your findings and commit them.
  2. Then open the sibling `2026-10-03-1151-board-split-cold.deferred.md` and
     the prior verdict in `docs/reviews/`, and write a *Reconcile* section.
  3. Fold the sibling in below the verdict and delete it.

  Use `python3 ../atelier/tools/coldsweep.py` for any search across the tree.
  It bars prior verdicts by default. A `--include-barred` run is disclosed in
  the verdict.
- **Decisions.** Findings on the doctrine parts are Mike's to decide (rule 3):
  the `CLAUDE.md` rules and the `docs/roadmap/README.md` legend. Record them,
  don't apply them. Findings on the conversion itself are ordinary records
  work: `[fixed]` only when the fix is re-driven, otherwise `[backlog]` or
  `[rejected: grounds]`.
- **Close-out.** Tick the queue pointer, rebuild the index and stage it with
  the item, and append a `docs/SESSIONS.md` entry. The repo is public, so the
  verdict is published the moment it is pushed. Keep it public-grade.
