- [ ] 🎯 **Board-split cold-pass follow-ups — RB1–RB12, five of them Mike's rulings.** Consolidated from the
      verdict on [`060/070`](070-cold-pass-queued-on-the-board-split.md) (2026-10-17 2113 UTC, PASS-WITH-FINDINGS,
      0 MAJOR, 12 MINOR; full text and counselled fixes in
      [`docs/reviews/2026-10-03-1151-board-split-cold.md`](../../reviews/2026-10-03-1151-board-split-cold.md)).
      Nothing below has been applied; the pass recorded and this item routes. One line per finding here — the
      record holds the evidence.
    - 🎯 **Mike's rulings (doctrine by function: the `CLAUDE.md` rules and the board legend) — recorded, not applied:**
      - **RB1** — `CLAUDE.md` § *Keep docs in sync* inlines the parent's BS1 residual ("the hook compares worktree
        to worktree"); false since 2026-09-20 (the hook runs `board --check --staged` from atelier `main`), and it
        contradicts this repo's own legend. Counsel: delete the parenthetical, point up to `CONCURRENCY.md` § *On a
        split board*; general rule — a child never inlines a parent's *residual* into standing text.
      - **RB2** — "the inlined floor differs from canon at `0af3006` in exactly two places" is false by one: the
        *Estate resources* bullet reads as an assertion where canon reads as a conditional (since `e527d06`,
        2026-07-30). Counsel: restore the canonical conditional, or correct the four records to "three places".
        **Settled 2026-10-26 by the `0a2b7a7` pin bump** (see `060/010`). The principal's 2026-09-19 ruling
        (*"Floor copy verbatim"*) leaves only one answer: the copy is canonical, so the conditional is back.
        The four records stay as written. They were true of their own day except for this miscount.
        That reading of his ruling is the bump session's, not his: it is put to him for confirmation
        (2026-10-26), and RB2 stays open here until he gives it.
      - **RB6** — the legend omits the first-physical-line projection rule (a bold title must close on line 1);
        `060/080` already trips it. Counsel: one sentence in `docs/roadmap/README.md`, then reflow `080`'s line 1.
      - **RB7** — atelier's rollout record has this repo's migration backwards ("born split, no prior roadmap";
        it was a 245-line root monolith and the least mechanical conversion in the fleet) and rests a doctrine
        inference on it. Handed up — see below. Mike's part: whether the 2026-08-17 hand-up he was left should have
        been routed then.
      - **RB11** — a recurring duty (the pin bump, `060/010`) is modelled as a one-shot `[x]` while drift stands at
        729 commits and the ritual's "read it, then bump" has no graceful form at that size. Counsel: a standing
        item carrying "pinned at X, drift N as of <date>", or a legend sentence making the drift check the trigger.
    - **[backlog] — conversion-record fixes, ordinary records work, each `[fixed]` only when re-driven:**
      - **RB3** — "pathscan back to its pre-split baseline of 5" does not reproduce under any tool revision (the
        delta added nine unmarked `missing-path` hits: relative-path references to the sibling repo). Counsel: scoped
        `pathscan:allow` markers on those lines; amend `060/060`'s verification line to the measured figures.
      - **RB4** — the `.pathscanignore` entry is inert (11 findings with or without it) and its rationale names
        generator shapes atelier fixed the same day. Counsel: delete the file.
      - **RB5** — the declared transformation set is incomplete (🛑/🎯 flags introduced, two leading ✅ dropped,
        one narrative sentence reworded, four first lines rewritten rather than reflowed; nothing lost). Counsel: one
        sub-bullet on `060/060` listing the full set.
      - **RB8** — the 2→6 re-indent *hid* the board from wrapscan (per-line ≥4-indent = code exemption): raw
        over-width lines rose 180 → 208 while the flagged count fell 133 → 38. The 2026-10-31 ruling on `060/030`
        would be made on a figure that no longer counts the board. Counsel: a note on `060/030` with the raw count.
        Handed up — see below.
      - **RB9** — `CONTRIBUTING.md` sends an outside contributor to `../atelier/tools/board.py` with no account of
        atelier or the sibling clone; CI's `board` check would fail their PR. The rebuild command is also spelled
        three ways (V4). Counsel: name the public atelier repo and the clone step, or "edit the item only; the
        maintainer rebuilds"; point the hand-written copies at the index preamble.
      - **RB10** — four substantially shipped items read `[ ]` because a residual rides inside them (`020/010`,
        `020/020`, `040/040`, `070/010`). Counsel: cut the residuals into leaf items. Low priority.
      - **RB12** — `38016b6` rewrote the inlined doctrine floor and landed with neither a queued pointer nor a
        `review:` line; the window ran 47 days until the brief-writer widened `070`. Counsel: add the review line to
        `060/010`'s 2026-08-17 sub-bullet pointing at `070`; fleet-wide, a retrofit of a stamped copy lands with its own line.
        The 2026-10-26 bump followed the counsel: it landed with its own pointer, `060/100`.
    - **Hand-ups filed to atelier (RB7, RB8)** under `PROPAGATION.md` § *Pointing up*, by this session, 2026-10-17:
      atelier board item `320/710` on a `report-` branch with its PR open — [PR #117](https://github.com/mike548141/atelier/pull/117). Filed, not merged;
      merging is the parent's call.
    - 🚩 **Routed to `050/060`, not a finding on the delta:** the claim-takeover text on `060/070` (this session's
      own commits and the two before it) publishes account-limit events — mild, and exactly the class that ruling
      asks Mike to decide.
      review: not warranted — a follow-ups item consolidating a landed verdict; the verdict is the review.
