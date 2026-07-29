# Review — post-flip cold review: what did going public create, and is the floor honoured?

## Brief

**The work under review**: the 2026-07-29 flip of this repo to PUBLIC (authorised in
[ADR 0009](../decisions/0009-publish-safety-review.md)) — everything that flip published
and every new surface it created — plus the repo's compliance with the atelier operating
model: is the enforcement chain (hook, CI floor, hatches, declarations, signing) honoured
in substance, or worked around?

**Spawn provenance** (REVIEW.md rule 4 shape, stated for auditability): spawned by the
principal directly, in a fresh session with cold context. The principal's ask, verbatim:
*"do a cold full review to look at any issues or concerns we may have created by making
the repo public"*, then *"Is this repo honouring the guardrails and policy as code I've
built in atelier and this repo? Its not working around them?"*. The reviewing session
authored none of the work under review (the flip, ADR 0009, and all prior commits were
other sessions' work); its own in-cycle fixes are marked as such below and were made on
the principal's explicit instruction.

**Recording honesty**: this file was written *after* the review ran, at the principal's
instruction, reconstructing the brief from the ask above — not pre-written before the
pass. The verdict below is the review as it actually unfolded, including its own errors
(see *Reconcile*), not a tidied re-derivation.

**Scope**: the four lenses over the widest scope the work admits — the published tree,
the full pushed history, the GitHub-side repo settings and workflows, the enforcement
chain end to end, and the repo's records. Non-goals: none declared.

**Assumptions attacked**: (a) that ADR 0009's six gates were sufficient cover for a
publication event; (b) that a green floor means the floor is being honoured rather than
bypassed; (c) that the repo's guardrail declarations match atelier's current doctrine.

---

## Verdict

**0 MAJOR · 11 findings — 3 fixed in-cycle, 3 fixed by a follow-on session before this
record was written (see *Reconcile*), 4 backlog, 1 awaiting the principal. The flip
published nothing it should not have, and the enforcement chain is honoured in substance
— the debts found were staleness, visible by design, not circumvention. Per REVIEW.md's
close rule, a pass with no MAJOR closes the cycle.**

### Proofs re-run (never taken from the record)

ADR 0009's claims were re-derived, not read: an independent sweep of **every blob in
every pushed commit** for secret patterns and personal/estate terms — clean, matching
the ADR. Beyond it: the floor executed locally from atelier's live registry (all
blocking scanners pass); the signed range verified (22/22 good signatures since the
declared boundary); hook installation confirmed in this clone (`core.hooksPath`,
resolvable scanner path, fail-closed); floor + CI observed green on both tips this
review pushed. The one recorded claim *not* re-run: ADR 0009's planted-canary proof of
secretscan cover (grounds: repeating it plants a live-shaped secret in a now-public
working tree for no new information; the original is recorded with its firing evidence).

**Security-scanner line** (REVIEW.md lens 4): `/security-review` reads pending diffs;
this is a landed-state review with no diff in scope, so the scanner could not be aimed
at the work — discharged with grounds; the history/tree sweeps above are the mechanical
floor this review layered under lens 4 instead.

### Findings

Lens 4 — security & privacy (each with severity + recurrence prevention, per REVIEW.md):

- **F1 · minor · [fixed]** The committed `.claude/settings.json` published the exact
  command allow-list AI sessions run unprompted, while going public opened untrusted
  inbound (issues/PRs) into those sessions — mapping prompt-injection from a guess to a
  plan. Fixed: untracked + gitignored (commit `b0a6618`); the historic copy remains in
  published history and cannot be unpublished. Recurrence prevention: the gitignore
  entry with its stated reason; the allow-list *trim* (destructive verbs) is the
  remaining half — ROADMAP.
- **F2 · minor · [backlog]** The wiki is enabled: a separate git repo the scanner floor
  never sees — an unscanned publication channel. Recurrence prevention on action:
  disable it; unused surfaces stay off. ROADMAP.
- **F3 · minor · [backlog]** Release supply chain: a third-party action pinned by
  mutable tag inside the job holding `contents: write` + `id-token: write` (the
  provenance-signing credentials); allowed-actions policy is "all", no SHA-pin
  requirement, Dependabot off. Recurrence prevention: SHA-pin + Dependabot
  (`github-actions` ecosystem) so pins stay current mechanically. ROADMAP.
- **F4 · minor · [fixed]** No vulnerability-reporting channel for a tool that writes to
  raw block devices under sudo. Fixed: GitHub private vulnerability reporting enabled
  (verified via API) + `SECURITY.md` (commit `e481b6c`). Recurrence prevention:
  SECURITY.md is now the standing route; REVIEW.md already requires security findings
  in shipped tooling to route through it.
- **F5 · minor · ⏳ principal** Estate-internal context accumulates in this repo's
  public records (session log naming sibling repos and their scan states; the
  model-economics doc publishing internal workflow). A records-convention question —
  doctrine by function, so the principal's to decide, not this review's (REVIEW.md
  rule 3): accepted transparency, or a public-repo convention change. ADR it either
  way; the ruling applies to the other repos heading public. ROADMAP carries it.

Lens 2 — correctness & quality:

- **F6 · minor · [fixed]** Pre-existing flaky CI test surfaced while verifying this
  review's own push: `test_block_sweep_in_benchmark_block` asserted exit 0, but with no
  card class known the tool honestly grades the medium against the A1 floor (ADR 0004)
  and a shared runner's disk under O_DSYNC genuinely dips below it (measured: 8.3 MBps
  seq / 54 write IOPS vs the 10 MBps / 500 IOPS targets). The tool was right; the test
  conflated its contract (JSON shape) with CI disk speed. Fixed (`15589f6`), fix
  live-verified: full matrix green on that tip.

Lens 3 — completeness / harvest (the guardrail audit):

- **F7 · minor · [fixed — follow-on session]** The atelier doctrine pin was 341 commits
  stale, and the session-start drift ritual had not been run (this review ran it).
  Scanners auto-propagate, so enforcement was current; *doctrine* travels only via the
  pin. Fixed 2026-07-30 by a follow-on session (`e527d06`): pin bumped to `e45549a`.
- **F8 · minor · [fixed — follow-on session]** `.atelier-floor.json` used the pre-C1
  bare-list advisory spelling — no `why`/`review-by` — flagged 🟡 by floor.py on every
  run and a hard error at C1 phase 2. Resolved 2026-07-30 on the owner's call
  (`3531829`, corrected by `0237ac9`): spellscan's debt cleared outright (15 US
  spellings) and the check returned to enforced; wrapscan declared advisory with a
  stated reason and `review-by: 2026-10-31`.
- **F9 · minor · [backlog → atelier]** The floor's ci plane invokes leakscan without
  `--require-terms`, so every child run self-reports "cover not guaranteed". The fix
  belongs in atelier's registry, not any child. ROADMAP points it upward.
- **F10 · minor · [backlog → publish-safety checklist]** ADR 0009's six gates cover
  what the repo *contains*; none covers what the platform *settings* expose (wiki,
  actions policy, fork-PR approval, vulnerability reporting, rulesets) — every
  settings-level finding above walked through that gap. Before `ros`/`faves` flip, the
  checklist this repo piloted should gain a GitHub-side-settings gate. Routes to where
  the checklist lives.
- **F11 · minor · [fixed — follow-on session] — a finding this review missed.** The
  doctrine block inlined in CLAUDE.md was three bullets short of atelier's canonical
  floor (concurrency, session rhythm, estate resources all absent — a retrofit gap
  nothing was watching, since stampscan is deliberately unwired). This review audited
  whether the floor was *enforced* and never diffed the inlined floor against canon;
  the pin-bump session found and fixed it (`e527d06`). Recorded here as a completeness
  miss of this pass, not a claim on its credit.

Lens 1 — approach & assumptions: assumption (a) *held with the F10 caveat* — content
cover was sound and independently reproduced; settings cover was the gap. Assumption
(b) held: the green floor reflects real enforcement (hook present and fail-closed,
hatches narrow and reasoned, backstop green independently of the hook). Assumption (c)
failed in three places, as F7/F8/F11 record — declarations and the inlined floor lagged
doctrine without breaching it.

### Reconcile — read after this review's findings were committed

Between this review's findings landing (`0260529`, `15589f6`) and this record being
written, a follow-on session resolved F7, F8 and F11 (`e527d06`, `3531829`, `0237ac9`).
Per REVIEW.md rule 2's shape, that work was read only after this review's own findings
were durably committed; the tags above reflect the reconciled state.

Reconciliation also surfaced **two measurement errors in this review's own published
figures** (ROADMAP/SESSIONS text at `0260529`): it reported the advisory debt as "8 US
spellings, ~40 over-width lines" — the true counts were **15** and **716**. The review
read only the tail of a truncated floor output and generalised it. The follow-on
session's correction (`0237ac9`) also re-diagnosed what the 716 means: a corpus-wide
~110-column style, not accumulated debt — a diagnosis this review got wrong in the same
direction. Both stand corrected here; the lesson (count from the full output, not the
visible tail) is the kind stampscan-style mechanical checks exist for.

### Decision trail

[fixed] findings were verified live, whoever fixed them: F1, F4 by API state + green
floor on the pushed tip; F6 by the green matrix; F7/F8/F11 by the pulled commits, the
current `.atelier-floor.json`, and the follow-on session's recorded floor-green run.
[backlog] findings (F2, F3, F9, F10) are consolidated in ROADMAP under *Public-repo
hardening* and *Floor & doctrine hygiene*. F5 waits on the principal, flagged in
ROADMAP as ADR-worthy. Cycle: **closed** (0 MAJOR).
