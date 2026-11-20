# 2026-10-26 — Doctrine catch-up: pin `0af3006` → `0a2b7a7`

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 46+1 -->
- [2026-10-26 · Doctrine catch-up: pin `0af3006` → `0a2b7a7`](2026-10-26-1013-doctrine-catch-up.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `f56c5d5`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-10-26** — **Doctrine catch-up: pin `0af3006` → `0a2b7a7`, floor re-stamped verbatim.** A headless session,
  started on Mike's instruction to bring every repo that is behind on doctrine up to date. Measured: 921 atelier
  commits; 18 files changed under `docs/method/`, all read in full. The previous entry deliberately held the bump
  because RB1, RB2 and RB11 are Mike's rulings. His instruction today is the go for the bump itself. RB2 is
  settled by his own 2026-09-19 ruling (*"Floor copy verbatim"*). RB1 and RB11 are **untouched** and still his.
  🔎 **What bore on this repo:**
  - **The floor copy must be verbatim** (`PROPAGATION.md` § *The standard child doctrine block*). This repo's
    block had three in-block differences: the *pushed*-floor-run sentence, the "a push is publication" warning
    in the visibility bullet, and the estate bullet's assertion form (RB2). The block is now the canonical
    region, wrapped in `stamp` markers, with the four placeholders filled. The two repo sentences sit
    beneath it under *Beneath the floor*. Hand-check against `origin/main`: **0 drift lines**, 3 placeholder
    fills, no residual placeholders. `stampscan` itself still exits on a config error for any child
    (`missing-source`, atelier's open ST3), so the hand-check is the instrument. That limit is known upstream,
    so it is not handed up again.
  - **Canon grew to nine bullets**: *asking* (the structured question device; options, trade-offs and a
    recommendation owed) and *doctrine problems point up* (report to atelier, never work around in silence).
    Concurrency now says read `git status` before the pull, never autostash a peer's work, and read the whole
    staged index with `git diff --cached`. The drift check now fetches and measures `..origin/main`.
  - **The model rule moved again**: ECONOMICS (2026-09-19) says the cheapest model that does a good job runs
    every seat; a session states its tier and does not ask. That widens `060/050`'s conflict, so a note was
    added there. The fix it already names is unchanged.
  - **Taken in, with no local action**: the APEX ask contents (options, a recommendation, verified facts);
    the COMMUNICATION decision device; plainscan retired (not in this repo's floor config); sizescan's length
    advisory dropped; GUARDS' fourth requirement and the mandate-or-default rule for dates; EVIDENCE §15 (a
    test cannot falsify its own code's assumption); REVIEW's standing checklist and the side-door rule;
    TOOLBOX's published expected-toolbox list; RECORD's identifiers block (used below); the session-open
    prompt history. None needs a mechanical change here.
  **Not done, on purpose:** RB1 (the BS1 parenthetical in `CLAUDE.md` § *Keep docs in sync* is false since
  2026-09-20) is recorded as Mike's ruling on `060/090`, so it stays until he rules. No claim was taken: the
  pin-bump item `060/010` is a closed one-shot (RB11), and the work landed as one commit. The rule-4 cold pass is
  queued at `060/100` with no brief (this session wrote the bump). It is Fable-tier and waits for Mike's approval.
  **Next:** Mike's rulings on `060/090`; the wrapscan ruling on `060/030`, due 2026-10-31; the `060/100` pass
  once Fable is approved; the v1.0 Pi-hardware blocker stands.
  **Identifiers**
  - Session: `b5fafd75-83f2-46d3-9a16-bf299fa05fd6`, Opus 5.5, headless, 2026-10-26 ~09:50–10:30 UTC.
  - Commits: the landing commit for this entry (it cannot name itself).
  - Pull requests: none.
  - Board: closed none; created `060/100` (⏳); notes added to `060/010`, `060/050`, `060/090`.
  - Worktrees and branches: `~/worktrees/rpi-pin-bump`, branch `doctrine/pin-bump-0a2b7a7`, merged to `main`
    and removed at close.
  - Agents: none launched.
  - Other repos: none written. The atelier checkout was read only, via `origin/main`.
