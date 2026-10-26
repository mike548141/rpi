- [ ] **Rewrap the wrapscan backlog to 85 columns — a cheap tidy, a few files
      at a time.** Queued 2026-10-27 from Mike's ruling on `060/030` (85 for
      new writing, history exempt). Do **not** mass-rewrap in one pass. Take a
      file whenever it is open for other work.
      - **The backlog: 108 flagged lines.** `docs/ARCHITECTURE.md` 41,
        `docs/MODEL-ECONOMICS.md` 27, `docs/roadmap/README.md` 8, the `050`
        narrative 5, and one first line in each of 27 board items.
        `MODEL-ECONOMICS.md` is due for a rewrite on `060/050`, so leave it
        to that.
      - **Done when** `wrapscan` reports 0. Then drop the `advisory` entry from
        `.atelier-floor.json`, so wrapscan is enforced again. Its `review-by`
        is 2026-12-31.
      - 🚩 **What "checked" does not reach.** wrapscan reads only `docs/` by
        default, so the root docs (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
        `SD_CARDS.md`, `SECURITY.md`; 259 raw over-width lines) are not
        checked at all. It also skips board-item body lines, which are indented
        6 columns, as if they were code (RB8 on `060/090`). So the board is
        checked on first lines only. Widening either is a scope choice to
        put to Mike, not part of this tidy.
