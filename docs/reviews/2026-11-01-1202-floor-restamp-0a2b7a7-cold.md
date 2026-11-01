# Cold pass — the floor re-stamped at `atelier@0a2b7a7`

**Pass type:** rule-4 cold pass, per atelier `docs/method/REVIEW.md` rule 4. The
delta is doctrine by function: the inherited safety floor in `CLAUDE.md` and this
repo's additions beneath it, which bind every session here.
**Tier:** Fable, the principal-named review tier (ruling 2026-08-04), **checked at
selection by the session that takes this**. A session not on that tier stops here and
takes nothing (rule 4, stop clause).
**Fable-gated:** the principal's standing ruling of 2026-10-26 is that no Fable work
runs without his explicit approval, and that such work waits for it rather than
running on a lesser tier. This pass runs **only on his explicit approval**.
**Status:** BRIEF WRITTEN 2026-11-01 1202 UTC. Not yet claimed, not yet run.
**Queue pointer:**
`docs/roadmap/060-floor-doctrine-hygiene-to-do/100-cold-pass-owed-the-0a2b7a7-floor-restamp.md`.
**Why it earns a review:** the floor is the block that binds even if atelier is never
read. A copy that reads as canonical but is not, a fill that carries more than a
fact, or a local rule that moved out of the block and changed meaning on the way,
alters what every later session here believes it must stop and confirm, and nothing
downstream complains. The repo is public, so each push of the delta was publication.

## Spawn provenance

- **Author of the work under review:** a headless Opus 5.5 doctrine catch-up session
  on 2026-10-26 (item `060/010` names it by session id), which landed the delta and
  queued the pointer. The later same-surface commit named under *What the work is*
  came from a further session on 2026-10-27 applying the principal's rulings.
- **Who wrote this brief:** an Opus 5.5 subagent (`claude-opus-5-5`) dispatched on
  2026-11-01 UTC by a Mike-opened Opus 5.5 orchestrating session (`2be3482c`) working
  from another repo, on the principal's instruction of 2026-11-02 NZDT: *"Write
  briefs for anything that needs a review in any of the repos, where a brief is not
  ready"*. Neither is the author's session, was started or instructed by it, or has
  edited any of the delta's paths.
- ⚠️ **Off-tier, disclosed rather than resolved.** The brief-writer forms no finding
  and assigns no severity. Everything this brief says is attackable, including what
  it says the work is and its non-goals. The reviewer may widen any of them, and says
  so in the verdict when it does.
- **Brief-writer's exposure, disclosed** (material read before writing): the queue
  pointer; the message bodies of `f56c5d5`, `cd41c64` and `102e909`; the `--stat` of
  each; `f56c5d5`'s hunks to `CHANGELOG.md` and item `060/010`; `cd41c64`'s
  `CLAUDE.md` hunk; item `060/030` whole; `CLAUDE.md` at HEAD below the stamp;
  `.wrapscanignore`; the earlier brief `2026-10-03-1151-board-split-cold.md` above
  its first divider, as a template; atelier's `REVIEW.md` excerpts and `review-brief`
  skill. It did **not** open `docs/SESSIONS.md` (the intent record) or either prior
  verdict beyond its file name. It ran each re-run line once; its results, and its
  own questions, are in the sibling
  `2026-11-01-1202-floor-restamp-0a2b7a7-cold.deferred.md` (2 sections: re-run
  results, 9 questions), never here.
- **Who takes the review:** a fresh session Mike opens on the Fable tier, which
  repeats its own provenance in the verdict. Barred: the authoring sessions; session
  `2be3482c` and its subagents, this brief-writer included.
- **Orchestration shape.** Preferred: reviewer plus orchestrator, where the taking
  session can spawn a Fable subagent; the session holds the sibling and releases it
  once the subagent's findings are committed. Single-seat, the deferral is a default
  with an audit trail and no partition (rule 1). Say in the verdict which shape ran.

## What the work is

Review the paths at HEAD (`102e909` or later).

- `f56c5d5` (2026-10-26, parent `e6bd0a3`): doctrine: bump the pin
  `0af3006`→`0a2b7a7`, and re-stamp the inlined floor verbatim. Paths: `CLAUDE.md`,
  `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/SESSIONS.md`, items `060/010`, `060/050`,
  `060/090` and this pointer `060/100`. **This is the pointer's delta.**
- `cd41c64` (2026-10-27): its `CLAUDE.md` hunk adds a rule beneath the floor (*never
  copy a parent's temporary gap into standing text*, on the principal's RB1 ruling)
  and replaces a board-check note with a pointer to atelier. **Not in the pointer's
  delta**; the brief-writer adds it because it edits the same beneath-the-floor
  surface the pointer names. Its commit carries `review: not warranted — recording
  two principal rulings and a measurement`; whether that holds for the `CLAUDE.md`
  hunk is yours to accept or reject. The widening itself is attackable.
- **Doctrine surface:** the `stamp:begin` … `stamp:end` block (lines 1–97 at HEAD)
  and the *Beneath the floor* list under it. **Canonical:**
  `../atelier/docs/method/PROPAGATION.md`, the region between `<!-- floor:begin -->`
  and `<!-- floor:end -->`, at `0a2b7a7`.
- **Intent record:** the 2026-10-26 entry in `docs/SESSIONS.md` (and the 2026-10-27
  entries for `cd41c64`); item `060/010`'s 2026-10-26 sub-bullet.
- **Machine-local, so no CI review sees it:** the floor and the board tool are
  atelier's, run from a sibling checkout through `git config hooks.atelierTools`.
  Establish what CI runs in their place from `.github/workflows/floor.yml`.

## Claims the delta makes, extracted (not evaluated)

From `f56c5d5`'s message, `CHANGELOG.md`, item `060/010` and the *Beneath the floor*
preamble, at HEAD:

- R1. 921 atelier commits; 18 files changed under `docs/method/` (1,580 lines added,
  132 removed); all read in full.
- R2. The block is atelier's canonical region with only the four placeholders filled,
  between `stamp` markers; a hand diff against `origin/main` shows 0 drift lines,
  three placeholder fills and no residual placeholders.
- R3. Three in-block differences left the block: the *pushed*-floor-run sentence and
  the "a push is publication" warning now sit beneath it; the *Estate resources*
  bullet is back to the canonical conditional, which settles RB2 on `060/090`.
- R4. Canon grew from seven bullets to nine (asking; doctrine problems point up);
  concurrency now says read `git status` before the pull and the whole staged index;
  drift is measured against `origin/main` after a fetch.
- R5. `stampscan` still cannot pass a child (it cannot resolve the `source=` path
  from a child's root; atelier's open ST3), so the diff is by hand.
- R6. The cheapest-model ruling widens `060/050`'s conflict, and a note was added
  there.
- R7. Docs only; no code change.

## Scope

Widest the work admits: intent, decisions, assumptions, the doctrine text, tooling
wiring and live behaviour. The lenses organise it and do not bound it. **Non-goals**,
each itself reviewable:

1. Whether atelier's canonical floor at `0a2b7a7` is *right*: atelier's own cycle
   reviews it. Its **copy and application here** are in scope.
2. Whether the pin is current *today*. atelier has moved since; that is the next
   bump's question. This pass judges fidelity to the pin chosen, and whether the bump
   carried what the 921 commits ask of a child.
3. `102e909` (2026-10-27, the wrapscan exemption on the principal's `060/030` ruling)
   and the rulings on RB1/RB2 as such. They are adjacent, carry their own review
   lines, and are not the pointer's delta. Where they bear on the floor's application
   here, say so.

**Drive these, don't read them:**

- **Fidelity.** Extract the canonical region at `0a2b7a7` and the stamped block at
  `f56c5d5` and at HEAD; diff them. Every differing line must be a placeholder fill.
  Judge each fill against the placeholder's meaning.
- **What left the block.** Take the block at `e6bd0a3` and account for every line
  that is not in the canonical region: carried beneath the floor, dropped, or
  replaced. Every change of meaning is a finding or has recorded grounds.
- **What the bump owed.** List the `docs/method/` files changed in `0af3006..0a2b7a7`
  in atelier. Decide for yourself what each asks of a child before you read the
  intent record; then check what the delta applied, boarded or left.
- **The floor's own instructions, live.** Run the drift check exactly as the block
  words it, from the primary checkout and from a `git worktree` of this repo, and say
  what each prints.
- **The floor and board at HEAD**, on both planes, as the hook and CI invoke them;
  get the exact form from `.githooks/pre-commit` and `.github/workflows/floor.yml`.

## The four lenses

1. **Approach & assumptions.** Name the load-bearing assumptions yourself, before
   reading the work's own account of why.
2. **Correctness & quality.** Check each claim R1–R7 against the tree; re-count every
   figure.
3. **Completeness / harvest.** Every surface in this repo that describes the floor,
   the pin or the drift check (`CLAUDE.md` below the stamp, `CONTRIBUTING.md`,
   `README.md`, `docs/ARCHITECTURE.md`, `docs/MODEL-ECONOMICS.md`, the board
   `README.md`s): does any still describe the old block, and is anything duplicated
   rather than pointed at?
4. **Security & privacy** (mandatory). The repo is public and every push of this
   delta was publication. Check that nothing in the re-stamped block, the fills or
   the beneath-the-floor list names a private repo, an estate detail or personal
   data, and that the publication warning that moved out of the block still binds
   where a session reads it. `/security-review` is discharged by grounds: the delta
   is landed and markdown-only, which the scanner's exclusions bar. Say so in the
   verdict and do the design-altitude read by hand; never run it over this brief.

## Re-run obligation

Re-run, do not read. The brief-writer ran each line once on 2026-11-01 UTC from a
worktree at `102e909`, with atelier at `7bd98ce`; its results are in the sibling. A
proof that does not reproduce is a finding. Use an absolute path to atelier when
working from a worktree outside the sibling layout.

```sh
A=<absolute path to an atelier checkout>; X=<your scratch dir>
git -C "$A" show 0a2b7a7:docs/method/PROPAGATION.md \
  | awk '/<!-- floor:begin -->/{f=1;next} /<!-- floor:end -->/{f=0} f' > "$X/canon.md"
awk '/<!-- stamp:begin/{f=1;next} /<!-- stamp:end -->/{f=0} f' CLAUDE.md > "$X/copy.md"
git show f56c5d5:CLAUDE.md \
  | awk '/<!-- stamp:begin/{f=1;next} /<!-- stamp:end -->/{f=0} f' > "$X/copy-f56c5d5.md"
diff "$X/canon.md" "$X/copy.md"; diff "$X/copy-f56c5d5.md" "$X/copy.md"
git log --oneline f56c5d5..HEAD -- CLAUDE.md
python3 "$A/tools/floor.py" --plane ci --root . --tools "$A/tools"
python3 "$A/tools/board.py" --check --root .
```

## Landing the verdict

- Append the verdict to this file below a `---` divider. Findings get stable IDs
  `FS1`, `FS2` and so on, each with a severity (MAJOR or MINOR) and a counselled fix
  where you can. Close with PASS, PASS-WITH-FINDINGS or FAIL.
- **Sequence:** (1) write your findings and commit them; (2) then open the sibling,
  the intent record and the prior verdicts in `docs/reviews/`, and write a
  *Reconcile* section; (3) fold the sibling in below the verdict and delete it. Use
  atelier's `tools/coldsweep.py` for any search across the tree; it bars prior
  verdicts by default, and a `--include-barred` run is disclosed in the verdict.
- **Decisions.** Findings on the floor and the beneath-the-floor rules are Mike's to
  decide (rule 3): record them, don't apply them. Findings on the records (board,
  changelog) follow the ordinary `[fixed]` / `[backlog]` / `[rejected: grounds]`
  route.
- **Close-out.** Claim the pointer first (`[~]`, stamp from `date -u` in the same
  command, pushed before work starts). At the end, mark the pointer, rebuild the
  index and stage it with the item, and append a `docs/SESSIONS.md` entry. The repo
  is public: the verdict is published the moment it is pushed. Keep it public-grade.

---
