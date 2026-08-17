- [ ] 🚩 **`docs/MODEL-ECONOMICS.md` repeats and CONTRADICTS house doctrine.**
      Queued 2026-08-09 from atelier's estate-wide duplication audit. This item previously read *"this repo's file is its own document, not a
      doctrine pointer, so nothing is stale"*, and treated the question as a cosmetic rename. **That claim was
      false**, and is corrected here rather than quietly replaced, because it is precisely what kept the file
      unexamined: 69 lines, **zero references pointing up**, self-described as *"Adapted from the sibling
      `ros`/`tiki` policy"* — a copy of a copy, and the sibling it came from carries the same defects.
      Mike ruled the governing rule 2026-08-09 (atelier `docs/method/PROPAGATION.md` § *Who is a child, and what a
      child may hold*): a child may **add** freely, may **never repeat** doctrine the parent owns, and may **never
      conflict** with it absent a specific principal ruling recorded here. Two of these are conflicts, not repeats:
      - **The two-pool billing table** (`Plan-included` vs `Usage-billed`, Fable 5 pinned to usage-billed "real
        money") was superseded by billing-state-of-the-marginal-token — billing state belongs to the *token*, not
        the model, and a plan can move the same model between plan-included, capped and usage-billed over time.
        It has. This file states as standing fact something that must be read off the current plan at session open.
      - **The fixed model-to-role mapping** ("Opus the workhorse, Fable the reviewer") was replaced by
        tier-by-risk: the seat is assigned by the work's capability needs and risk, never by which pool is cheaper.
      Also stale: the price table, the model names (Opus 4.8), and "cache TTL is 5 minutes" as the only TTL.
      **This repo is PUBLIC**, which raises the cost of leaving it — the stale prices and superseded model are
      published claims, and a reader has no way to tell a drifted copy from current guidance.
      Not theoretical: a sibling's copy of this same document *"drifted 17 days behind a provider change, and
      misled a session into arguing from a falsified fact"*. That sibling has since been trimmed to repo-local
      facts and is the worked recipe. **Fix:** keep only what atelier cannot hold — this repo's own measured read
      path, its own applications, and the no-live-hardware review caveat, which is genuinely repo-local and worth
      keeping — and replace every restated rule with a pointer to atelier `docs/method/ECONOMICS.md` read at the
      pin. Delete the billing table and the role mapping outright rather than correcting them: a corrected copy is
      still a copy, and drifts again at the next provider move. Do the `→ docs/ECONOMICS.md` rename in the same
      pass (atelier renamed its own in `b639513`), so the link churn is paid once.
