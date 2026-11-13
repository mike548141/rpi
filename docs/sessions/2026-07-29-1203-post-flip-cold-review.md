# 2026-07-30 — Cold post-flip review and guardrails audit

> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `0260529`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-30** — **Cold post-flip review + guardrails audit** (Mike's ask: what did going public create,
  and is the repo honouring the atelier floor or working around it). **Review verdict — the flip itself is
  clean**: an independent re-sweep of every blob in every pushed commit (on top of ADR 0009's) found no secret
  patterns and no personal terms; the concerns are all *new-surface* ones — untrusted inbound (issues/PRs)
  meeting a published command allow-list, the wiki as an unscanned publication channel, mutable-tag actions in
  the release job that holds the provenance-signing credentials, no vulnerability-reporting channel, and
  estate context accumulating in this public session log (ruling owed, see ROADMAP). **Audit verdict —
  honouring, not working around**: hook active and fail-closed in this clone, CI floor green on every push,
  every hatch narrow with a stated reason, signing verified back to the boundary, advisory softening only on
  the two checks the registry permits. Debts found, none hidden: the atelier doctrine pin is **341 commits
  stale** (scanners auto-propagate, doctrine does not — the pin ritual exists for exactly this);
  `.atelier-floor.json` is the **pre-C1 legacy spelling** (🟡 every floor run, hard error at C1 phase 2); the
  wrapscan/spellscan advisory debt is real and uncleared (8 US spellings, ~40 over-width lines). **Fixed now
  on Mike's instruction**: 🚀 private vulnerability reporting enabled + `SECURITY.md` added (GitHub advisories
  as the channel); `.claude/settings.json` untracked and gitignored — session policy is not for publication
  (the historic copy stays in published history; untracking stops future edits publishing). **Everything
  else** is captured in ROADMAP as to-dos (two new sections: public-repo hardening; floor & doctrine hygiene).
  **Next**: the roadmap hardening items; the pin catch-up as its own session; the standing v1.0 Pi-hardware
  blocker unchanged by all of this.
