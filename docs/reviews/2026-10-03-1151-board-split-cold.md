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

---

# Verdict — 2026-10-17 2108 UTC (2026-10-18 NZ)

## Provenance

- **Author of the work under review:** the 2026-08-17 session (commit
  trailers: Claude Opus 5, 1M context) that landed `4bd429c`, `0679384` and
  `38016b6`.
- **Brief-writer:** an rpi session on Opus 5.5, 2026-10-03/04, off-tier and
  disclosed as such in the brief above. It formed no finding.
- **Reviewer (this text):** a fresh Fable subagent (`claude-fable-5-1`),
  spawned headless by the orchestrator session `rpi-63`, itself a headless
  Fable session Mike opened and pointed at the queue. The orchestrator held
  the `.deferred.md` sibling, forms no finding and writes no severity; it
  read the sibling at its own session open, before this reviewer existed, as
  the queue pointer discloses. Neither seat authored the delta or was started
  or instructed by its author.
- **Orchestration shape:** reviewer-plus-orchestrator. **The sibling was not
  opened before these findings were committed.** It was removed from the
  reviewer's working copy for phase 1 (`git status` shows it ` D`); the
  reviewer did not `git show` it or any other revision of it.
- **Spawn note for the audit trail:** this is the third run on this claim.
  The two earlier headless runs died before writing anything; the pointer
  records both takeovers. Nothing from them was available to read.
- **What this reviewer read.** The brief; the queue pointer `060/070`; atelier
  `docs/method/REVIEW.md` in full, `skills/review-brief/SKILL.md`, `RECORD.md`
  § *The roadmap*, `CONCURRENCY.md` § *Claiming work* (which holds *On a
  split board*), and the board-store ADR with its three amendments;
  `docs/SESSIONS.md` lines 373–428 only (the two 2026-08-17 entries);
  `docs/ROADMAP-DONE.md`'s delta hunk only; the full delta diff
  `eb66c2f..38016b6` and the three commit messages; `eb66c2f:ROADMAP.md`;
  every file under `docs/roadmap/` at HEAD and at `4bd429c`; `docs/ROADMAP.md`
  at `eb66c2f`, `4bd429c`, `38016b6` and HEAD; `.githooks/pre-commit`,
  `.github/workflows/floor.yml` here and atelier's reusable `floor.yml`,
  `.atelier-floor.json`; atelier's `tools/board.py`, `harvestscan.py`,
  `floor.py`, `wrapscan.py` and `pathscan.py` as code (today's and the
  revisions `2428fdf` and `0af3006`, extracted to scratch); PROPAGATION.md's
  canonical floor block at `0af3006`; atelier's board item
  `010/030-fleet-rollout-of-the-split-board.md` (a record, not a verdict) and
  grep hits naming `rpi` across atelier's board files; GitHub's run list for
  this repo's `floor` and `ci` workflows. **Barred material opened: none.**
  Every tree search ran through `coldsweep.py` at its default bar; no
  `--include-barred` run. Two scanner outputs named a line *in* a barred file
  (the pin-era pathscan listed a `missing-path` hit at
  `docs/reviews/2026-07-29-…:64` and two in `docs/SESSIONS.md`); the files
  were not opened. The prior verdict, the sibling, and atelier's own
  board-store verdicts (`010/050` and the like) were not opened.

## Lens 1 — approach & assumptions

**Load-bearing assumptions, named before reading the work's account of why**
(then tested — the result is beside each):

- *A1 — the per-item store was the right shape for a 245-line board.* The
  ADR's read-cost argument does not apply here and the work says so itself.
  What does apply: state asserted in prose glyphs no scanner could read
  (verified — the original has **0** checkbox-grammar lines, so every
  scanner that reads items saw an empty board), and uniformity with a fleet
  that split the same day. On a principal's instruction, and with that
  grounding, it was the right change. The cost accepted: a session wanting
  detail opens N files instead of one; for 29 items that is cheap.
- *A2 — the `[x]`/`[ ]` classification read off each bullet is sound.* I
  classified all 27 migrated bullets from `eb66c2f:ROADMAP.md` **before**
  looking at the split's choice: `[x]` for 020/030, 030/010, 030/020,
  040/010, 040/020, 040/050, 060/010, 060/020, 070/020, 070/030 (10) and
  `[ ]` for the other 17. The split chose identically, 27/27. Two were
  judgement calls either way (040/040 *Publish an SBOM* — wired, unpublished
  until the tag; 030/040 *Grow the CID database* — a standing theme with no
  closure criterion) and the split's `[ ]` is the conservative reading of
  the legend's own rule. ✅ Holds.
- *A3 — the 2→6 re-indent is lossless.* Verified by multiset (below) and by
  the house net (`harvestscan --against eb66c2f`, clean). ✅ Holds, with one
  side-effect the record did not see (RB8).
- *A4 — the `board` check genuinely enforces on both planes.* Registry at
  atelier HEAD: `hook=["--check","--staged",…]`, `ci=["--check",…]`,
  `advisory=None`. Hook plane re-run green; GitHub's floor green on all three
  delta commits. ✅ Holds — and holds *better* than the doctrine text in this
  repo says (RB1).
- *A5 — the legend describes the parser truthfully.* `harvestscan.CONT_RE`
  is `^\s{4,}\S` and a non-blank line under 4 columns ends the item
  (`parse_items`, the final `elif`). ✅ Holds. The legend is silent on one
  rule the migration itself had to work around (RB6).
- *A6 — every surface that pointed at the roadmap was repointed.* Swept
  (lens 3). ✅ Holds for every path reference; generic "ROADMAP" mentions
  remain as a noun and still resolve to the board.
- *A7 — the retrofit left the inlined floor byte-identical to canon at the
  pin apart from two declared places.* ❌ Does not hold (RB2).

**The brief's framing, attacked.** Its widening to `38016b6` was right: that
commit rewrote `CLAUDE.md` doctrine text and regenerated the index, and
reviewing `4bd429c` alone would have reviewed a `CLAUDE.md` that no longer
exists. Its three non-goals are honest narrowings; none fences off a risk the
work carries. One thing the brief under-stated: it treats the index generator
as "machine-local, so no CI review sees it" — in fact CI *does* run `board
--check` from atelier `main` on every push, so the generated index is CI-
reviewed; what is machine-local is only *which revision* of the tool a hook
runs. That distinction turned out to matter (the re-run table).

## Lens 2 — correctness & quality

Each declared transformation, checked:

| Declared | Result |
|---|---|
| 245-line root `ROADMAP.md` → 7 sections, 29 item files (27 + 2) | `wc -l` 245 ✅ · `find` 29 ✅ · 7 dirs ✅ · 33 top-level bullets of which 6 are the preamble's companion-doc list ⇒ 27 ✅ |
| a mechanical split would have produced zero items | `grep -cE '^\s*-\s+(\[[ x~]\]\|⏳)'` over the original = **0** ✅ |
| checkbox read off text, `[x]` only where nothing outstanding | 27/27 agree with an independent read (A2) ✅ |
| bodies verbatim apart from a uniform 2→6 re-indent | multiset of non-heading lines, leading whitespace and link depth normalised: 219 original lines, 15 differ, all 15 map to a rewritten line in the store, none lost ✅ — but the rewrites are more than the record declares (RB5) |
| four items given a bold title or reflowed first line | 070/010, 070/020, 070/030, 060/050 — found; they are *rewrites*, not reflows (RB5) |
| index projects the first physical line only | true of `board.py` (`item_state` + `index_title`); every migrated item closes its bold title on line 1 ✅; the first item added after the split does not (RB6) |
| `.pathscanignore` for the generated index, which cannot carry an inline marker | true at landing (the index then emitted both false-positive shapes); the generator fixed both the same day and the entry is now inert (RB4) |
| `docs/ROADMAP-DONE.md` frozen | freeze note present; `sizescan` clean on archive stores ✅ |
| the inlined floor differs from canon at `0af3006` in exactly two places | **three** (RB2) |

Hairlines, recorded without a finding ID: the CHANGELOG entry says "(docs
only; no code change)" while two source files changed — comment lines only,
no behaviour; `38016b6`'s message does not say it regenerated the index,
though its stat does (and it had to — the tool moved under it); the `⏳`
pointer as queued carried "whose own review cycle was open on BS1 when this
landed", a hair past refs-only, which `pointerscan` accepted.

## Lens 3 — completeness / harvest

Surfaces that name the roadmap's location or how the board works, swept with
`coldsweep.py --root . 'ROADMAP'` plus a hand read of the man page, packaging,
CI, settings and `tools/`:

- Repointed by the delta: `CLAUDE.md` (ritual, status, keep-in-sync, open
  threads), `README.md` ×3, `CONTRIBUTING.md` ×3, `docs/ARCHITECTURE.md`,
  `docs/MODEL-ECONOMICS.md`, `docs/ROADMAP-DONE.md`, `bench.py`, `cli.py:42`.
  All resolve (`linkscan` clean) ✅.
- Left as a generic noun, still true: `cli.py` lines 118, 559, 634, 1395
  ("see ROADMAP"), `release.yml:5`, `docs/ARCHITECTURE.md:86`, ADR 0009:14,
  `SD_CARDS.md:102`. Not findings.
- `docs/rpi-sdinfo.1`, `pyproject.toml`, `.github/workflows/ci.yml`: no
  roadmap reference to repoint ✅.
- Outside the repo, for the orchestrator: the agent's auto-memory file
  `rpi-sdinfo-preferences.md` still says "keep README.md, ROADMAP.md … in
  sync" — a machine-local mirror, not a publication matter.
- Atelier's record of this rollout (`010/030`) describes rpi **wrongly** —
  RB7. This repo's intent record explicitly left that hand-up to Mike and it
  was dropped between the two repos.
- Duplicated rather than pointed at: the rebuild command is hand-written in
  `CLAUDE.md` and `CONTRIBUTING.md` in one spelling and generated into the
  index in another (RB9).

## Lens 4 — security & privacy

**`/security-review` — discharged by grounds.** This is a landed delta; its
~50 files are markdown, which the scanner's own exclusions bar, so a clean
pass would be definitionally empty; its two `.py` hunks are one comment line
each. It was not run. The design-altitude read was done by hand instead:

- `git diff eb66c2f..38016b6 | grep` for `/Users/`, `/home/`, a home-dir
  marker or a Windows drive: **none**. The generated index names no path
  (`rebuild_cmd` emits the hook's own resolution order, by design).
- Estate references: `../atelier` by relative path only, as `CLAUDE.md`
  prescribes; the principal's first name and GitHub handle, already the
  repo's established practice; no private-repo name, no inventory root.
- The ADR 0009 triage stands: a whole-tree `leakscan` on this machine
  reports 11 machine-local-term hits, every one on a pre-existing line
  outside the delta (copyright headers, packaging metadata); GitHub's floor,
  structural-only by design, is green. Not a finding on the delta.
- One observation **outside the delta** for the 050/060 ruling's domain:
  the claim-takeover text now in `060/070` (the orchestrator's commits)
  publishes two account-limit events. Mild, and exactly the class 050/060
  asks Mike to rule on.

## Driven checks — what was run, not read

- **Losslessness.** `eb66c2f:ROADMAP.md` vs `docs/roadmap/**` at `4bd429c`,
  the two new items excluded, as a Counter over non-heading lines with
  leading whitespace, the added checkbox and link depth normalised. 15 lines
  only-in-original; each has a rewritten counterpart (listed under RB5).
  Then the house net: `harvestscan --root . --against eb66c2f --records
  ROADMAP.md --survivor-store docs/roadmap` → *clean — every removed roadmap
  item still exists somewhere*.
- **Classification.** Independent read first, then compared (A2): 27/27.
- **The index.** Scratch copies via `git archive`. Today's `board.py`: HEAD
  regenerates byte-identical, `check` clean; `4bd429c` regenerates
  *differently* (banner, narrative link text, flag position). Then the tool
  as it stood at each landing: `board.py@2428fdf` (the pin `4bd429c`
  declared) → `4bd429c`'s index **current**; `board.py@0af3006` (the pin
  `38016b6` declared) → `38016b6`'s index **current**; `board.py@2428fdf`
  against `38016b6` → stale, i.e. the second commit regenerated under the
  newer tool, correctly. The diffs are tool drift, not a defect.
- **The floor, both planes.** Hook: `floor.py --plane hook --root . --tools
  ../atelier/tools` → exit 0, every enforced check ✅, `board` enforced.
  CI form: `floor.py --plane ci --root . --tools ../atelier/tools` → exit 1,
  **BLOCKED by leakscan** — but only because this machine holds the local
  term list that CI never has (the registry's own line: "cover not
  guaranteed — the ci plane does not pass --require-terms", item 060/040).
  What CI itself ran: `gh run list --workflow=floor.yml` — `4bd429c`,
  `0679384`, `38016b6` and every later push **success**; `ci.yml` success.
- **The ritual, from cold.** Step 1: `docs/ROADMAP.md` is 71 lines, every
  link resolves, the legend is one click away ✅. Step 2: not run (barred).
  Step 3: all three companions exist ✅. The drift check `git -C ../atelier
  log --oneline 0af3006..HEAD` returns **729 commits** — "read it, then bump"
  has no graceful form at that size, and the board shows no open item for
  the bump (RB11).

## Re-run obligations

| Claim (from the work's records) | Re-run | Result |
|---|---|---|
| floor green on the hook plane; `board` in scope and enforced | `floor.py --plane hook` at HEAD; `board.py --check` at each landing commit with the tool at its declared pin | ✅ reproduces |
| `harvestscan` clean over the split store | `--against eb66c2f --records ROADMAP.md --survivor-store docs/roadmap` | ✅ clean |
| `pointerscan` clean over the split store | at `4bd429c` with `pointerscan@0af3006` and today's; at HEAD | ✅ clean ×3 |
| 182 tests pass | `nice -n 10 python3 -m unittest discover -s tests` | ✅ Ran 182, OK (9.5 s) |
| pathscan back to its pre-split baseline of 5 after `.pathscanignore` | `pathscan@2428fdf`, `@0af3006`, `@HEAD` over `eb66c2f` and `4bd429c` scratch trees | ❌ **does not reproduce**: pin-era 4 → 11 (with the ignore; 19 without), today 1 → 8. See RB3 |
| 7 sections, 29 item files (27 + 2) | `find`, `ls` | ✅ |
| a purely mechanical split ⇒ zero items | grammar grep over the original | ✅ 0 matches |
| inlined floor differs from canon at `0af3006` in exactly two places | `diff` of the canonical block (placeholders filled) vs `CLAUDE.md` above the divider | ❌ **three** places. See RB2 |
| ruff not run at landing | `ruff check .` (0.17.1) | ✅ All checks passed |

## The standing checklist

- **V1 — no claim stronger than its evidence.** Bitten three times: the
  pathscan baseline (RB3), "exactly two places" (RB2), and the under-declared
  transformation set (RB5). Each is a record overclaim; none hides lost work.
- **V2 — every recorded proof re-run.** Done (table above); two failed.
- **V3 — a changed rule swept to every mirror.** The repointing is complete
  in-repo (lens 3). Two mirrors missed: atelier's rollout record (RB7) and,
  machine-locally, the agent memory note.
- **V4 — one fact, one home.** Bitten: the rebuild command hand-written in
  two files and generated in a third (RB9); a parent residual (BS1) copied
  into a child rule where it went stale (RB1).
- **V5 — no internal contradiction.** Bitten once: `CLAUDE.md` says the hook
  compares worktree to worktree; `docs/roadmap/README.md` says the check
  blocks a stale index unconditionally; the README is right today (RB1).
- **V6 — security & privacy.** Lens 4; discharged with grounds; one
  out-of-delta observation routed to 050/060.
- **V7 — spawn provenance stated.** In the brief, the pointer, and above.

## Findings

Severity is to *this delta's* cycle. Decision tags: doctrine parts
(`CLAUDE.md` rules, the `docs/roadmap/README.md` legend) are **🎯 Mike** —
recorded, nothing applied; conversion findings are `[backlog]` with a
counselled fix. Nothing was applied in this pass.

**RB1 — MINOR — 🎯 Mike.** `CLAUDE.md` § *Keep docs in sync* inlines a
point-in-time fact about the *parent's tool* into a standing rule: "at the
hook plane it compares worktree to worktree, so staging one without the other
slips past it — atelier's open BS1." True at the pin; false since 2026-09-20,
when `board --check --staged` landed in the registry the hook actually runs
(the hook resolves atelier at `main`, never at the pin). The rule now
mis-describes the live gate, and it disagrees with this repo's own legend,
which is right. Over-warns rather than under-warns, hence MINOR.
*Counselled fix:* delete the parenthetical; keep "stage the item and the
index together" as the habit and point up to `CONCURRENCY.md` § *On a split
board* for the guarantee. The general rule worth writing once: a child never
inlines a parent's *residual* into its own standing text — a residual is
dated by nature and nothing here watches it (stampscan is unwired).

**RB2 — MINOR — 🎯 Mike.** The retrofit's claim — "the inlined block now
diffs against PROPAGATION.md's canonical one at exactly two places: the pin
SHA, and this repo's own sentence" (commit `38016b6`, `CHANGELOG.md`,
`060/010`, the session log) — is false by one. The *Estate resources* bullet
reads "**This repo is public**, so reference the root by local-path
convention only" where canon at `0af3006` reads "If **this** repo is public,
reference the root by local-path convention". The divergence predates the
delta (`e527d06`, 2026-07-30) and is semantically faithful; the delta's four
records assert a byte-identity that was never there. *Counselled fix:* either
restore the canonical conditional (the visibility bullet two lines down
already asserts PUBLIC, so nothing is lost and the block becomes verifiable
byte-for-byte when stampscan is wired), or keep the wording and correct the
records to "three places". Floor text, so the choice is Mike's.

**RB3 — MINOR — [backlog].** "pathscan back to its pre-split baseline of 5
findings after a `.pathscanignore` entry" does not reproduce under any tool
revision: with the tool at either pin the tree went 4 → 11 (the ignore
removed the index's 8; it never touched the item files); with today's tool,
1 → 8. The split added **seven** unmarked `missing-path` findings, all one
class — relative-path references to atelier (`../atelier/tools/board.py` in
the legend and in `060/060`; the ADR in `060/070`) and to atelier-owned docs
paths quoted in `060/050`, plus `.claude/settings.json` in the 050 narrative
(untracked by design). Warn-only, so nothing blocked; the "verified" claim
is what is wrong. *Counselled fix:* scoped `<!-- pathscan:allow:missing-path:
sibling repo, by relative-path convention -->` markers on those lines (the
practice atelier's own board uses), and amend `060/060`'s verification line
to the measured figures. `080` will not help here — these are not `src/`
paths.

**RB4 — MINOR — [backlog].** The `.pathscanignore` entry is inert and its
rationale is stale. Its comment names two generator shapes — section links
whose *text* repeats the path, and a banner naming `tools/board.py` — that
atelier fixed the same day (`b2ba382`, `a3a64aa`; its rollout record says
`faves` deleted the identical pair). Measured at HEAD: 11 pathscan findings
with the file, 11 without. *Counselled fix:* delete the file; a generator
regression would then be visible again, which is what the warn-only scanner
is for.

**RB5 — MINOR — [backlog].** The declared transformation set is incomplete.
Beyond the checkbox, the re-indent and "four items got a bold title or a
reflowed first line", the split also: introduced a `🛑` on 010/010 and a
`🎯` on 040/030 and 050/060 (none carried the glyph; each is a fair reading
of "your call" / "Ruling owed", but it is editorial), and duplicated the
`🎯` on 030/030; dropped the leading `✅` from 060/010 and 060/020 where the
record says "the original glyphs were left standing in the body"; reworded
the 050 narrative ("the items below are" → "this section's items are" —
correct, since "below" lost its referent); and rewrote, not reflowed, the
four first lines (070/010: "optional true O_DIRECT path on Linux (aligned
buffers) for the most accurate…" → "a true O_DIRECT path on Linux. Optional,
with aligned buffers, for the most accurate…"). Nothing was lost — the
multiset and `harvestscan` both say so — and every edit improves the index.
The defect is the record reading "verbatim" where a future auditor will
find it was not. *Counselled fix:* one sub-bullet on `060/060` listing the
full set, so the next migration in the fleet declares its own.

**RB6 — MINOR — 🎯 Mike.** The legend omits the one rule the migration had
to work around by hand: the index projects the **first physical line** only,
so a bold title must close on it. The first item added after the split
(`060/080`, 2026-09-19) trips it — its index line reads "Declare this repo's
`pathscan` source root once atelier ships the", cut mid-sentence. The
parent's BS2 class, recurring here because the legend never said it.
*Counselled fix:* one sentence in `docs/roadmap/README.md` after the
continuation-indent paragraph; then reflow `080`'s state line (a records
edit, not doctrine).

**RB7 — MINOR here, material upstream — 🎯 Mike (hand-up).** Atelier's
rollout record (`docs/roadmap/010-…/030-fleet-rollout-of-the-split-board.md`)
tabulates rpi as "`4bd429c` | — → 69 | **born split** — no prior
`ROADMAP.md`" and builds on it: "`rpi` never migrated: it had no `ROADMAP.md`
before `4bd429c`, so its board was *written* in the store form from nothing.
That is the stronger evidence for the form — it is adoptable without a
monolith to convert, which no migration could have shown." Every clause is
false: `eb66c2f:ROADMAP.md` is a 245-line monolith at the repo **root** (the
record measured `docs/ROADMAP.md`, found nothing at the parent, and inferred
birth), and its conversion was the *least* mechanical in the fleet — zero
checkbox lines, a judgement per item — which also contradicts the same
record's "the cut needs no judgement". The rpi intent record saw this coming
and left the hand-up to Mike ("writing to another repo's queue from this
session was not asked for"); it was then recorded upstream, wrongly, from a
measurement that could not see a root-level file. MINOR to this delta
because the delta is correct and said the right thing; routed upward because
a doctrine inference now rests on it. *Counselled fix:* correct the row and
both inferences in atelier, and add rpi's glyph-grammar case as the
counter-example to "needs no judgement"; queue a one-line hand-up item on
this board so the routing is on the record.

**RB8 — MINOR — [backlog].** The 2→6 re-indent did not *add* to the wrapscan
debt as the record says; it **hid** the board from wrapscan. The scanner's
documented per-line rule treats any line indented ≥4 as indented code and
exempts it ("honest limit: this is blunt… it will also exempt some
genuinely-wrappable indented prose"). Measured: raw lines over 85 columns
rose 180 → 208 across the board, while wrapscan's flagged count fell
**133 → 38** (169 of the 208 are item bodies at 6 columns; the 38 are the
state lines and the legend). The 2026-10-31 ruling on `060/030` will be made
on a figure that no longer counts the board. *Counselled fix:* a note on
`060/030` giving the raw count and why the scanner's differs; and a hand-up
to atelier — every split-board body in the fleet is now wrapscan-exempt by
the same rule, which the tool documents as a limit but the split made
systematic.

**RB9 — MINOR — [backlog].** `CONTRIBUTING.md` now tells an outside
contributor to rebuild the index with `python3 ../atelier/tools/board.py
rebuild --root .` and says nothing about what atelier is or that a sibling
clone is needed; the `board` CI check will fail their PR if they edit an
item file without it. Pre-split a contributor edited one file. V4 as well:
the rebuild command is spelled one way by hand in `CLAUDE.md` and
`CONTRIBUTING.md` and another by the generator in the index preamble; the
tool already prefers `--rebuild` and the hand-written copies will drift.
*Counselled fix:* in `CONTRIBUTING.md`, name the public atelier repo and the
sibling-clone step — or say "edit the item file only; the maintainer rebuilds
the index" — and point both hand-written copies at the index's own preamble
instead of restating the command.

**RB10 — MINOR — [backlog].** Granularity carried over from the monolith:
four items that are substantially shipped read `[ ]` in the index because a
residual rides inside them — 020/010 (two residuals: wiring the corners
sweep; hardware validation), 020/020 (the suspicion-score ADR), 040/040
(waiting only on 040/030's tag), 070/010 (one O_DIRECT path). Correct under
the legend's work-owed rule, and a defensible "convert, don't re-cut"
choice; but `CONCURRENCY.md`'s fan-out rule means each is claimable only as
a unit, and the index under-reports delivered work. *Counselled fix:* cut
the residuals into leaf items and flip the parents `[x]`. Low priority.

**RB11 — MINOR — 🎯 Mike.** A recurring duty is modelled as a one-shot
item. `060/010` *Bump the atelier pin* is `[x]` — right at landing, bumped
that day — while the ritual's drift check at HEAD returns 729 commits and
the board shows nothing owed. The ritual's own wording ("read it, then bump
the pin deliberately") has no graceful form at that size either.
*Counselled fix:* either a standing `[ ]` item that carries "pinned at X,
drift N as of <date>" and is never closed, or a legend sentence saying the
drift check, not the board, is the trigger for a bump — Mike's call, since
both touch doctrine. Separately worth a word in the drift bullet: what to do
when the drift is too large to read.

## Verdict

**PASS-WITH-FINDINGS.** 0 MAJOR, 11 MINOR. The conversion itself is sound:
lossless by two independent measures, classified correctly on all 27 items
by an independent read, index current under the tool each commit was landed
with, hook and CI floors green, 182 tests and ruff clean. What the pass found
is in the *records* around the conversion (three verification claims that do
not reproduce, one under-declared transformation set, one upstream record
that describes this repo's migration as the opposite of what it was) and in
two doctrine lines that have aged out from under the tooling. Under the close
rule a pass with no MAJOR closes on application; the 🎯 items are Mike's.

Phase 2 (reconcile against the sibling and the prior verdict; fold; delete)
follows below once the sibling is restored to this working copy.

*Reviewer timestamp: 2026-10-17 2108 UTC.*
