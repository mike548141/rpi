- [x] **Resolve the wrapscan mismatch before 2026-10-31.** 716 over-width lines in `docs/` — but spread across
      *every* file, because this repo's prose is simply written at ~110 columns rather than the 85-column house
      width. That makes it a style mismatch spanning the corpus, not a backlog: it grows with every entry appended
      at the local style, and the 2026-07-30 session entry proved it by adding 35 more within minutes of the
      declaration being written. Two honest resolutions, and the review picks one: **adopt 85** for new prose and
      `.wrapscanignore` the frozen records, or **exempt this repo's prose** from the house width outright and say
      so. An expired `review-by` reds the fleet board and blocks nothing, so this is board pressure, not a gate.
    - **Measured 2026-10-27, on Mike's word ("measure first, then decide").**
      Lines over 85 columns, counted two ways. *Raw* counts every line in every
      tracked `.md` file. *Flagged* is what `wrapscan` reports: it reads only
      `docs/`, and it skips lines indented 4+ columns as if they were code.
      - **Frozen records** (`ROADMAP-DONE.md`, 2 reviews, 10 ADRs; 13 files):
        raw 543, flagged 395.
      - **Append-only logs** (`docs/SESSIONS.md`, `CHANGELOG.md`): raw 569,
        flagged 420. Old entries never change; new ones are added at ~110.
      - **Live prose** (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
        `SD_CARDS.md`, `SECURITY.md`, `ARCHITECTURE.md`, `MODEL-ECONOMICS.md`):
        raw 341, flagged 68. Five of the seven sit at the root, outside the scan.
      - **Board** (40 item and narrative files): raw 326, flagged 40. The 6-column
        body indent hides almost all of it (RB8 on `060/090`).
      - **Generated index** (`docs/ROADMAP.md`): raw 31, flagged 0. Link lines a
        tool writes; not hand-wrapped prose.
      - **Total: raw 1,810, flagged 923.** Raw includes tables, URLs and code,
        so not every line is fixable prose. Tool: atelier `tools/wrapscan.py`
        at `ffabef3`.
    - ✅ **Ruled 2026-10-27, closed.** Put to Mike as: *"rpi: line width. 85
      for new writing with history exempt, or exempt rpi entirely?"* He chose
      *"(a) 85 for new, exempt history (Recommended)"*. Applied:
      `.wrapscanignore` exempts the frozen records and the two running logs as
      whole files, with his answer as the reason. Live docs and board items
      stay checked.
      - **Tested, not assumed:** flagged fell 923 → **108**, which is
        923 − 395 − 420, and none of the 108 is in an exempted file.
        `CHANGELOG.md` is at the root, outside wrapscan's default `docs/`
        scan, so its glob is future-proofing.
      - The 108 left are the backlog on [`060/110`](110-rewrap-the-wrapscan-backlog.md).
        wrapscan stays advisory until that clears (`.atelier-floor.json`,
        `review-by` 2026-12-31).
