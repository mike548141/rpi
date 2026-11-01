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
**Status:** BRIEF WRITTEN 2026-11-01 1202 UTC. Claimed 2026-11-01 1349 UTC for the
Fable drain. **ACT 1 RUN 2026-11-01 UTC** on Fable 5.1 under an off-tier
orchestrator holding the partition: verdict below, PASS-WITH-FINDINGS (1 MAJOR,
6 MINOR), committed as `b99f868`. **ACT 2 RUN 2026-11-01 UTC** after the sibling
was released: reconcile below the verdict, one finding added (FS8), final verdict
PASS-WITH-FINDINGS (1 MAJOR, 7 MINOR). The sibling is folded in by the
orchestrator.
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
  results, 9 questions), never here. (Orchestrator, 2026-11-01: the sibling is now
  folded in at the end of this file, below the reconcile, and deleted.)
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

## Verdict — act 1, cold pass run 2026-11-01 UTC

**Reviewer:** Fable 5.1 (`claude-fable-5-1`), the principal-named review tier,
checked at selection. **Shape that ran:** reviewer plus orchestrator, partition
held. The reviewer was spawned by a headless Opus 5.5 orchestrating session, itself
started by drain session `c87c4ee0` (Opus 5.5); both are off-tier orchestrators
that hold the context partition, form no finding and write no severity. Neither is
a barred session: the brief bars the authoring sessions (`b5fafd75-…` and the
2026-10-27 session that made `cd41c64`) and session `2be3482c` with its subagents,
the brief-writer included. The reviewer was started and instructed by none of
them. It ran under the principal's weekly Fable-drain approval of 2026-11-02 NZDT.
**Partition:** the `.deferred.md` sibling was removed from the worktree before the
reviewer opened; it was not sought in history, other checkouts or scratch, and this
act was written without it. `docs/SESSIONS.md` and the two prior verdicts were not
opened. The sweep ran `coldsweep.py` with its default bar (4 barred paths, 5
files); no `--include-barred` run. **Disclosed exposure beyond the brief:** the
queue pointer `060/100` (read after the brief, as the brief's `Queue pointer`
line directs) carries three questions; they are the brief's own drives restated,
and FS4 below is about that door.

**Widenings taken, as the brief invites.** (1) `cd41c64`'s `CLAUDE.md` hunk is
reviewed as part of the delta: it adds a rule beneath the floor, which is doctrine
by function, so its `review: not warranted` line does not hold for that hunk; this
pass is the review it owed (FS5). (2) The floor's live behaviour was taken wider
than the drift check: the hook and CI planes were run at HEAD on this machine, and
`stampscan` was aimed at the block directly.

### Lens 1 — approach and assumptions, named before the intent record was read

- **A1. "Verbatim" is judged by `diff`, and the stamp markers are the unit.**
  Holds: the `floor:begin`…`floor:end` region at `0a2b7a7` is wrapped in a
  Markdown fence inside `PROPAGATION.md`, so the only non-placeholder lines the
  diff shows are the two fence lines, which are extraction artefacts, not text.
- **A2. The four placeholders are the whole licence to differ.** Holds. Canon
  carries four kinds (`<SHA>` twice, `<atelier-path>` three times,
  `<visibility fact>`, `<owner/repo>`), in three diff hunks. Both figures appear
  in the records as "placeholder fills" (FS7).
- **A3. A repo sentence that leaves the block keeps its meaning beneath it.**
  Holds for the two that moved (below). The assumption the delta did not test is
  whether a sentence beneath the floor may *repeat* what the parent owns (FS6).
- **A4. `../atelier` is where atelier is.** Holds only in the sibling layout. The
  floor's own concurrency bullet makes a worktree the default, and from a worktree
  laid out without an atelier sibling the fill resolves to nothing (FS2).
- **A5. The tools the floor runs are the pin's.** False, and worth saying: the
  hook and CI both run atelier's tools at `main`, through `hooks.atelierTools` and
  the reusable workflow's `atelier-ref`. The pin governs doctrine text only. A
  tool ruling landed inside the pin range therefore already binds here whether or
  not the bump noticed it (FS3).
- **A6. A rule added beneath the floor on a principal's pick is his ruling.** Not
  as written: the record shows the general rule was the reviewer's counsel and his
  pick was the specific fix (FS5).

### Lens 2 — correctness: R1–R7 re-counted against the tree

- **R1** (921 commits; 18 files; +1,580/−132): **reproduced exactly** by
  `git rev-list --count` and `git diff --stat 0af3006 0a2b7a7 -- docs/method/`.
  "All read in full" is unverifiable from the tree; not contested.
- **R2** (0 drift lines, three fills, no residual placeholders): **reproduced**.
  Canon at `0a2b7a7` against the HEAD block differs only in the three placeholder
  hunks, and no `<…>` placeholder survives in the copy. "Three fills" counts hunks;
  "four" elsewhere counts kinds (FS7).
- **R3** (three in-block differences left the block): **reproduced** by diffing
  the `e6bd0a3` block against canon: the *pushed*-floor sentence (session-rhythm
  bullet), the publication warning (visibility bullet), and the estate bullet's
  assertion form. Each is accounted for below.
- **R4** (seven → nine bullets; `git status` first and the whole index; drift
  against `origin/main`): **reproduced** in the canon diff.
- **R5** (`stampscan` cannot pass a child; `source=` resolution; ST3):
  **reproduced, and incomplete.** Aimed at `CLAUDE.md`, `stampscan` exits with a
  config error, `canonical source does not resolve: docs/method/PROPAGATION.md
  (resolved against --root …)`. Its *default* walk never reaches the block at all:
  it scans `<root>/docs`, and the stamp is in root `CLAUDE.md`, so the default run
  prints a clean pass over nothing and `--require-stamps` exits 2. Two reasons; the
  record names one.
- **R6** (a note added on `060/050`): **reproduced**, the 2026-10-26 sub-bullet.
- **R7** (docs only): **reproduced**; `f56c5d5` touches eight `.md` files and
  nothing else.

**Fills, judged against the placeholder's meaning.** `<SHA>` → `0a2b7a7`, both
sites, correct. `<owner/repo>` → `mike548141/rpi`, the public slug, correct.
`<visibility fact>` → a three-line fill: the fact (PUBLIC), its date
(2026-07-29), its grounds (the owner's instruction after ADR 0009) and a repo-local
link that resolves. More than a bare fact, but all of it is provenance *of* the
fact and none of it is a rule; accepted, not a finding. `<atelier-path>` →
`../atelier`: see FS2.

**What left the block, line by line.** (a) The *pushed*-floor sentence: now the
second beneath-the-floor bullet, meaning preserved; it drops the old conditional
"when the close pushes", which the parent's text carries, so the local line is now
slightly broader than its source (see FS6 for the repeat). (b) The publication
warning: now the first beneath-the-floor bullet, meaning preserved sentence for
sentence; it still binds where a session reads it, because `CLAUDE.md` is the first
file every session reads and the in-block visibility bullet sits twenty lines
above it. (c) The estate bullet's assertion ("**This repo is public**, so …")
reverted to canon's conditional, grounds recorded (RB2, ruled closed 2026-10-27);
the conditional's antecedent is true by the in-block visibility bullet, so nothing
narrows. (d) "shared estate tooling" left the estate list: a canon change, not a
repo sentence; `TOOLBOX.md` now owns it and the block points there. (e) The drift
command moved from `0af3006..HEAD` to a fetch and `..origin/main`: canon change,
applied.

**Pointers beneath the floor, checked at the pin.** `RECORD.md § Finish the
sequence` and `CONCURRENCY.md § On a split board` both resolve, but to bold
paragraph leads (lines 124 and 296 at `0a2b7a7`), not headings; a grep finds them,
a table of contents does not. `PROPAGATION.md § Who is a child` and § *Pointing
up* are headings. Noted, not a finding.

### Lens 2 — the floor's own instructions, live

- **Drift check from the primary checkout** (`../atelier` resolves to the sibling
  atelier checkout): fetch succeeds; `log --oneline 0a2b7a7..origin/main` prints
  **20 commits**. The pin is behind the parent's mainline today. That is the next
  bump's question (non-goal 2) and RB11's modelling question on `060/090`, said
  here so the record carries the figure.
- **Drift check from a `git worktree` of this repo** (the reviewer's own, laid out
  as `<dir>/rpi` with no `<dir>/atelier`): both commands fail,
  `fatal: cannot change to '…/../atelier': No such file or directory`. The
  reviewer did not `cd`; it passed the same relative path through `git -C`, which
  resolves identically. **FS2.**
- **`floor.py --plane hook`** at HEAD, nothing staged: clean apart from the
  declared advisory `wrapscan` (108) and the warn-only `pointerscan` (1) and
  `pathscan` (15). The hook plane scans the index, so it says nothing about the
  tree.
- **`floor.py --plane ci`** at HEAD on this machine: **BLOCKED by `leakscan`, 11
  findings**, all `local-term`, all on lines that already carry a generic
  `leakscan:allow:` marker (the author byline in `pyproject.toml`, five source
  headers, the man page, the archived script, ADR 0009 and one session-log line).
  The term is a machine-local one and is not named here. CI does not carry the
  term list (`cover not guaranteed — the ci plane does not pass --require-terms`),
  so the pushed floor is green on `main` through `2819a0c` (four runs, all
  `success`). **FS3.**
- **`board.py --check`**: index current, both planes.
- **`pointerscan`** flags `060/100` itself: `carries a question — a pointer names
  refs, it does not seed the pass's questions`. **FS4.**
- **`pathscan`**'s 15 are the known class (relative `../atelier/…` references,
  RB3), two of them in `060/010` and `060/100`; pre-existing, warn-only, no new
  finding.

### Lens 3 — what the bump owed, decided from the parent before the records

Read from the 18 changed files at `0af3006..0a2b7a7`, what each asks of a child:

- `PROPAGATION.md`: verbatim floor in stamp markers (**done**); `narrow=` reds on
  the floor (n/a, nothing narrowed); § *Pointing up* — a child's pending-upstream
  line is "dated, addressed, and removable at the next pin bump", and one that
  survives a bump past its parent item is drift (**FS1**).
- `CONCURRENCY.md`: the floor's two concurrency changes (**done** via canon); the
  `board` check now runs `--staged` at the hook, and `rebuild --from-index` is the
  dirty-checkout form (**pointed at** from `CLAUDE.md` since `cd41c64`; the inline
  command there still shows only the clean-checkout form, which the pointer
  covers); orchestration doctrine (scratch dirs, terminal markers, tier at open)
  is read on demand and asks nothing of the block.
- `ECONOMICS.md`: cheapest-model ruling of 2026-09-19 (**noted on `060/050`**,
  whose contradiction it widens; the file it indicts, `docs/MODEL-ECONOMICS.md`,
  is still open there since 2026-08-09 — boarded, not a new finding).
- `AUTONOMY.md`: the pin must be current at a visibility flip — this repo flipped
  2026-07-29, before the rule; nothing owed now.
- `GUARDS.md`: a fleet `review-by` names its kind (mandate or default); the only
  `review-by` here (`wrapscan`, 2026-12-31) is the repo's own; nothing owed.
- `RECORD.md`: identifiers block at close; a pending-review entry names deferred
  material by file and count only — session duties, not block text; the pointer
  names the sibling by file without a count, which is under the ceiling.
- `REVIEW.md`: side doors, the standing checklist V1–V7, the orchestrator shape
  — this pass's own duties; V3/V4 drive the sweep below.
- `00-APEX.md`, `COMMUNICATION.md`: the asking bullet (**done** via canon).
- `TOOLBOX.md`: the expected toolbox is atelier's; the floor points at it
  (**done**). `session-open/`, `DATA-PROTECTION.md`, `SECRETS.md`, `EVIDENCE.md`,
  `PRINCIPLES.md`, `README.md`: nothing a child's block or records must carry.

**Harvest (V3/V4): surfaces that describe the floor, the pin or the drift
check.** `coldsweep` over the tree for the stamp, pin, drift and `stampscan`
vocabulary: no surface outside `CLAUDE.md` and the board still describes the old
block or the old drift command. `CONTRIBUTING.md`, `README.md`,
`docs/ARCHITECTURE.md` and `docs/MODEL-ECONOMICS.md` do not describe the floor at
all. `CONTRIBUTING.md:20` and `docs/roadmap/README.md:9` carry the
`../atelier/tools/board.py` path (RB9's surface, open). The one duplication found
is FS6.

### Lens 4 — security and privacy

- **`/security-review` discharged by grounds:** the delta is landed and
  Markdown-only, a file class the scanner's exclusions bar, so its clean pass
  would weigh as nothing; it was not run, and never over this brief.
- **Design-altitude read, by hand.** Threats for this class (doctrine text in a
  public repo): a silent narrowing of the floor — none, 0 drift lines; a fill
  carrying private detail — none: the fills name a public slug, a date, a
  repo-local ADR and `../atelier` (atelier is public and already named in
  `.github/workflows/floor.yml`); a beneath-the-floor line naming a private repo,
  an estate fact or personal data — none; a pointer to nowhere — `linkscan`
  clean. The in-block visibility bullet and the publication warning directly
  beneath it are both on the first surface a session reads.
- **The publication warning still binds** where it moved to (lens 2 (b) above).
- **One class routed, not found:** the claim text on `060/100` (not in the
  pointer's delta; written 2026-11-01) says the pass runs "for Mike's weekly Fable
  drain, under his approval". `060/090` already routes publication of
  account-limit events to `050/060` for the principal's ruling; this is the same
  class and goes with it.
- **Machine-local term hits** (FS3) are all on lines already published by design
  (the author byline ships in PyPI metadata); no new exposure, and the term itself
  is not written here.

### Findings

Findings on the floor and the beneath-the-floor list are the principal's to
decide (rule 3); they are recorded with a counselled fix and nothing is applied.
Findings on the records take the ordinary route.

- **FS1 — MAJOR (principal's).** `CLAUDE.md:117–119`, the fourth
  beneath-the-floor bullet, reads *"diff the copy against the canonical region
  at the new SHA by hand, because `stampscan` is not wired for children yet"*.
  That is a parent's temporary gap ("not yet built", atelier's open ST3) written
  into this repo's standing text — exactly what the third bullet, added in
  `cd41c64` on the RB1 ruling of 2026-10-27, forbids five lines above it. The
  rule also fails
  `PROPAGATION.md` § *Pointing up* step 3's form for a pending-upstream line: it
  is undated and names no parent item. It goes false the day atelier wires
  `stampscan` for children, and nothing here will notice; `stampscan`'s default
  walk does not even reach the block (R5 above), so the hand diff is the only
  check and the line that mandates it is the one that will rot. Severity rests on
  the self-contradiction in a doctrine surface, not on the harm, which is bounded:
  the worst case is a session hand-diffing when a tool could. **Counsel:** keep
  the instruction and drop the reason — *"Pin bumps re-stamp the floor verbatim
  and diff the copy against the canonical region at the new SHA; use `stampscan`
  where it passes a child (atelier ST3), by hand until then. Record each bump on
  `060/010`."* — or point at `060/010`, which already holds the ST3 note as dated
  history.
- **FS2 — MINOR (principal's).** The `<atelier-path>` fill `../atelier` fails in
  the layout the floor itself prescribes: the concurrency bullet makes a worktree
  the default, and from a worktree with no atelier sibling the drift check's two
  commands exit `fatal`. The failure is loud, so the cost is a session that knows
  it could not run the check, not one that believes it did. The hook already
  solves the same problem: `hooks.atelierTools` is repo config, shared by every
  worktree, and resolved to the sibling atelier checkout here. **Counsel:** one
  beneath-the-floor sentence, *"From a worktree without an atelier sibling,
  `../atelier` is the parent of `git config --get hooks.atelierTools`"*; or lay
  worktrees out beside an atelier worktree, if the house's worktree tool can.
  Either is the principal's, because it touches how the floor's own command is
  read.
- **FS3 — MINOR (records route).** Eleven lines carry a generic `leakscan:allow:`
  marker that no longer covers them: atelier's D1 ruling (2026-08-04, inside the
  pin range) made the machine-local term layer immune to generic markers, and the
  2026-08-09 hatch requires the scope to name `local-term`. On this machine the
  whole-tree floor is red, and a commit that stages any of the eleven files will
  block at the hook until the marker is widened. CI stays green only because it
  carries no term list. The bump was the catch-up occasion and did not run the
  tree-wide floor. **Counsel:** `leakscan:allow:local-term: <reason>` (composed
  with the existing scope where one is needed) on the eleven lines; re-run
  `floor.py --plane ci` on a machine with the term list and record the figure.
- **FS4 — MINOR (records route).** The queue pointer `060/100`, written in the
  landing commit `f56c5d5`, carries three questions under **The questions**.
  `REVIEW.md` rule 4 makes the pointer refs only — "a ceiling as well as a floor"
  — and `pointerscan` flags it. A reviewer's onramp reads the pointer before the
  brief, so the questions are a side door the deferral cannot close; here they
  restated the brief's drives and steered nothing, which is disclosed above.
  **Counsel:** strip the three sentences from the pointer; the brief holds them.
- **FS5 — MINOR (principal's).** `cd41c64`'s `CLAUDE.md` hunk adds a general rule
  beneath the floor and attributes it to *"Mike's ruling, 2026-10-27, on RB1"*.
  The record on `060/090` shows the general rule was the cold reviewer's counsel;
  his pick was *"(a) Delete it, point to atelier"*, the specific fix. Citing an
  agent's generalisation as his ruling is the attribution error the house guards
  against, and the commit's `review: not warranted — recording two principal
  rulings` does not hold for a hunk that encodes a rule the session worded; this
  pass is the review it owed. The rule itself is sound and the parent half-owns it
  (§ *Who is a child*; § *Pointing up* step 3). **Counsel:** either he confirms the
  general rule as his, and the bullet keeps its citation, or the bullet reads
  *"adopted 2026-10-27 on his pick of RB1's counsel"*.
- **FS6 — MINOR (principal's).** The second beneath-the-floor bullet restates
  `RECORD.md`'s rule that a close which pushes carries the pushed floor run's
  result. The parent owns that rule (its *Finish the sequence* bullet, grounded
  2026-07-23), and `PROPAGATION.md` § *Who is a child* says a child may add but
  never repeat. It was a defensible local addition while the block compressed
  session rhythm; moved out of the block it is a repeat with a pointer, and it has
  already drifted by a conditional (lens 2 (a)). **Counsel:** reduce it to the
  pointer, or delete it, since the floor's session-rhythm bullet already names
  `RECORD.md`.
- **FS7 — MINOR (records route).** The records disagree on the fill count: the
  commit message and `060/010`'s hand-check line say three placeholder fills; the
  beneath-the-floor preamble, `CHANGELOG.md` and `060/010`'s opening say four.
  Both are true of different things (three hunks, four placeholder kinds, seven
  tokens), and a later reader cannot tell which. **Counsel:** one sentence on
  `060/010`: "four placeholders in three hunks".

### Verdict

**PASS-WITH-FINDINGS — 1 MAJOR, 6 MINOR.** The copy is the canonical floor at
`0a2b7a7` word for word apart from the placeholder fills; every sentence that left
the block is accounted for and kept its meaning; the bump applied what the 921
commits asked of a child's block and boarded what it widened. The defects are in
the list beneath the floor (FS1, FS5, FS6), the one fill that does not survive the
floor's own default layout (FS2), and the records and tooling around the delta
(FS3, FS4, FS7). Nothing in the delta names a private repo, an estate detail or
personal data. The pushed floor is green on `main`; the local whole-tree floor is
red on this machine for a reason the delta did not cause and did not catch.

## Reconcile — act 2, run 2026-11-01 UTC after act 1 was committed (`b99f868`)

Opened in this order, only after act 1 was pushed: the held sibling (released by
the orchestrator), then the intent record (`docs/SESSIONS.md`, the 2026-10-26 entry
and the two 2026-10-27 entries), then the prior verdicts
`2026-07-29-1251-post-flip-cold-review.md` and `2026-10-03-1151-board-split-cold.md`.
Nothing above this heading was changed by what they said; where a finding moves, it
is said here.

### The sibling's re-run results against this pass's

All six agree. (1) 95-line region with two fence lines, four placeholders in seven
occurrences: same. (2) three hunks at HEAD, `f56c5d5` block identical to HEAD: same;
the sibling's 22 diff lines were not counted here, the hunks match. (3) three-line
visibility fill: same. (4) `cd41c64` the only `CLAUDE.md` commit since: same.
(5) CI-plane floor on this machine blocked by `leakscan`, 11 `local-term`,
`secretscan` 30 advisories: same, run from a different worktree and a later atelier
tools revision. The sibling left the pushed run unchecked; this pass checked it:
`success` on every `main` tip from `f56c5d5` through `b99f868`. (6) board exit 0:
same. No proof failed to reproduce.

### The sibling's nine questions, answered

1. **Three or four fills?** Both counts are in the record, including both in the
   2026-10-26 session entry itself. Three is hunks, four is placeholder kinds,
   seven is tokens. **FS7** stands; the counsel there is the one-sentence fix.
2. **Is a link a fact?** The fill is the fact (PUBLIC) plus its provenance (date,
   grounds, a repo-local ADR link that `linkscan` resolves). A reader of the floor
   alone gets the fact without following the link; the link adds nothing a rule
   would. Accepted in lens 2, no finding.
3. **Worktree drift check: copy, canon or hand-up?** The copy: canon's placeholder
   is neutral and the fill chose `../atelier`. **FS2** stands as the principal's.
   The same fill will fail the same way in every child that uses it, so a one-line
   note in `PROPAGATION.md`'s fill guidance is a reasonable hand-up; that is
   unevidenced beyond this repo and is offered, not filed.
4. **Is adopting a general rule a record or doctrine?** Doctrine by function; rule 4
   binds it, and this pass is the review it owed (the brief widened to it). **FS5**
   stands, and the prior verdict sharpens it (below).
5. **Does § *On a split board* say what the removed note said?** No, and that is
   the point: at `0a2b7a7` it says the hook runs `board --check --staged` since
   2026-09-20, the opposite of the note it replaced. The pointer is right; the
   target is a bold paragraph lead at line 296, not a heading (lens 2).
6. **Does a block-only reader learn that a push is publication?** Not from the
   block: canon's visibility bullet carries the fact and canon's estate bullet the
   reconnaissance warning, and a child may add nothing in-block. The warning sits
   in the same file, directly beneath the stamp, which every session reads first.
   Whether the house wants a push-is-publication sentence *inside* the floor for
   public children is atelier's call and a possible hand-up; unevidenced here.
7. **Does the wrapscan exemption match the ruling for new entries?** `102e909` is
   outside the pointer's delta (non-goal 3). The exemption does cover new entries
   in both logs; `060/030` says so plainly ("wrapped at 85 by habit, not by this
   check") and `060/110` carries the scope question. Honest, recorded, not a
   finding here.
8. **Did the landing pass the hook, and does the record carry the pushed run?**
   The record does not say whether the hook ran, and nothing in the tree can.
   The one `docs/SESSIONS.md` term hit predates the delta (`5b3d753`). The pushed
   runs for `f56c5d5`, `cd41c64` and `102e909` are all `success`. The 2026-10-26
   close, which moved the pushed-floor rule beneath the floor, does not carry a
   floor result in its all-clear or identifiers. **FS8, below.**
9. **Was `060/050`'s widened conflict carried as a finding or a note?** A note; the
   item's fix was already on record from 2026-08-09 and is unchanged. Right call,
   and this pass leaves it boarded (lens 3).

### The intent record against this pass

- The 2026-10-26 entry's list of what the 921 commits asked of a child matches the
  independent list in lens 3 item for item; nothing it took in without action
  needed one. It names the `stampscan` limit as "known upstream, so it is not
  handed up again", which is right for a record and does not reach **FS1**: the
  defect is the same limit written as standing doctrine in `CLAUDE.md`.
- The 2026-10-27 entry says *"His general rule went in Beneath the floor"*. The
  prior verdict (RB1, below) shows the general rule was the reviewer's counsel and
  his pick was the specific fix. **FS5** stands; only he can say whether his pick
  carried the rule.
- The entry also notes atelier's "a child may not repeat" rule already covers the
  RB1 rule. That is **FS6**'s ground applied to the neighbouring bullet.
- The record carries no claim that this pass's findings contradict; FS2, FS3 and
  FS4 are about what it did not measure or did not say.

### The prior verdicts against this pass

- **2026-10-03, RB1.** Its counsel ends: *"The general rule worth writing once: a
  child never inlines a parent's residual into its own standing text — a residual
  is dated by nature and nothing here watches it (stampscan is unwired)."* Two
  consequences. It confirms **FS5**'s reading of where the rule came from. And it
  makes **FS1** the same class recurring inside the commit series that applied RB1:
  the residual it names in passing is the one `f56c5d5` promoted to standing text.
- **2026-10-03, RB2.** Counselled restoring the canonical conditional so the block
  "becomes verifiable byte-for-byte when stampscan is wired"; the bump did that,
  and this pass's diff is the byte check it anticipated, by hand.
- **2026-10-03, RB11** and its reconcile observation 3 (tooling does not follow the
  pin). Both open; this pass's 20-commit drift figure and assumption A5 are the
  same facts a month on.
- **2026-10-03, RB12.** Counselled that a retrofit of a stamped copy lands with its
  own pointer; `f56c5d5` did, which is why this pass exists.
- **2026-07-29, F7 and F11.** The pin was 341 commits stale and the block three
  bullets short; `stampscan` "deliberately unwired" was first recorded there. Both
  were fixed by `e527d06`; this pass finds the block whole and the pin 20 behind.
- No finding of this pass is withdrawn or re-graded by the prior verdicts.

### Finding added in reconcile

- **FS8 — MINOR (records route) — formed after the sibling was opened, from its
  question 8.** The 2026-10-26 close moved the rule *the close's all-clear carries
  the pushed floor run's result* beneath the floor and did not meet it: the entry's
  all-clear and identifiers block name commits, board items, worktrees and agents,
  and no floor result, pending or final. The run was green (`f56c5d5`, `success`,
  2026-10-26 10:13 UTC), so the gap is in the record, not the tree. **Counsel:**
  a dated note on `060/010`'s 2026-10-26 sub-bullet naming the pushed run's
  result; going forward, the identifiers block carries "floor at head: <result>".

### Verdict after reconcile

**PASS-WITH-FINDINGS — 1 MAJOR, 7 MINOR** (FS1–FS7 from act 1 unchanged; FS8
added here and marked as formed after the sibling was opened). The sibling's six
re-runs reproduce; its nine questions are answered above, three of them by findings
already recorded (FS2, FS5, FS7), one by a new one (FS8), the rest by grounds.
Decisions: FS1, FS2, FS5 and FS6 are the principal's; FS3, FS4, FS7 and FS8 take
the ordinary records route. The sibling is to be folded in below this section by the
orchestrator and deleted in the same commit.

---

## Deferred sibling, folded below the verdict (orchestrator, 2026-11-01)

Folded by the off-tier Opus 5.5 orchestrator, which forms no finding, after act 2
was saved. Below is the brief-writer's `.deferred.md` sibling, verbatim: it was
held out of the worktree from before the reviewer started until act 1 was
committed (`b99f868`), then released to the reviewer for the reconcile above.
Its heading levels are demoted one step so that they nest under this section; no
other character is changed. The sibling file itself is deleted in the same commit.
Two of its lines run past 85 columns; they are left as written.

## Sibling to the floor-restamp-0a2b7a7 cold pass — held under rule 1's split

Sibling of `docs/reviews/2026-11-01-1202-floor-restamp-0a2b7a7-cold.md`, held under
atelier `docs/method/REVIEW.md` rule 1's split. **Open only after the phase-1
findings in the brief are committed.** Written 2026-11-01 UTC by the Opus 5.5
brief-writer named in the brief's provenance; it forms no finding and writes no
severity. Fold this file in below the reconcile and delete it.

### Re-run results held back from the brief

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

### Brief-writer's questions, for reconcile

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
