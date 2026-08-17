- [ ] **Resolve the wrapscan mismatch before 2026-10-31.** 716 over-width lines in `docs/` — but spread across
      *every* file, because this repo's prose is simply written at ~110 columns rather than the 85-column house
      width. That makes it a style mismatch spanning the corpus, not a backlog: it grows with every entry appended
      at the local style, and the 2026-07-30 session entry proved it by adding 35 more within minutes of the
      declaration being written. Two honest resolutions, and the review picks one: **adopt 85** for new prose and
      `.wrapscanignore` the frozen records, or **exempt this repo's prose** from the house width outright and say
      so. An expired `review-by` reds the fleet board and blocks nothing, so this is board pressure, not a gate.
