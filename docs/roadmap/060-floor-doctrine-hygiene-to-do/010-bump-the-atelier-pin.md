- [x] **Bump the atelier pin.** Done 2026-07-30: `9e7e031` → `e45549a`. The drift also exposed that this repo's
      inlined floor was never the canonical seven bullets — concurrency, session rhythm and estate resources were
      all missing, a pre-existing retrofit gap nothing was watching (stampscan, the scanner built to catch exactly
      this, is deliberately unwired). Detail in `docs/SESSIONS.md`.
    - **2026-08-17**: `e45549a` → `2428fdf` → `0af3006`, twice in one session — atelier landed 28 further commits
      while the board split was being built, three of them touching `docs/method/`. Two retrofits followed, both
      of the same class the 2026-07-30 bump found: the **Three Laws were removed from the house apex**
      (2026-08-15), with the principal's absolute authority and the re-brief-before-an-irreversible-action rule
      standing in their place; and the **channel** landed as a concurrency primitive, widening the canonical
      concurrency bullet. The inlined floor is now byte-identical to
      `../atelier/docs/method/PROPAGATION.md`'s canonical block apart from the pin SHA and one local addition
      (the close's all-clear carries the *pushed* floor run's result). Still nothing mechanical watching this —
      stampscan remains unwired, so each bump's retrofit is found by hand or not at all.
    - **2026-10-26**: `0af3006` → `0a2b7a7` — 921 atelier commits, 18 files changed under `docs/method/`
      (1,580 lines added, 132 removed), all read in full. A headless doctrine catch-up session (id
      `b5fafd75-83f2-46d3-9a16-bf299fa05fd6`, Opus 5.5) did it on the principal's instruction. What it moved here:
      the inlined floor is **re-stamped word for word** from `PROPAGATION.md`'s `floor` region and wrapped in
      `stamp:begin`/`stamp:end` markers. That is the principal's 2026-09-19 ruling (*"Floor copy verbatim"*):
      a child's floor copy is never compressed or narrowed. So this repo's three in-block differences left the
      block. The *pushed*-floor-run sentence and the "a push is publication" warning now sit beneath it as
      local additions. The *Estate resources* bullet is back to the canonical conditional, which settles RB2
      on `090`. Canon itself grew from seven bullets to nine: **asking**, and **doctrine problems point up**.
      Concurrency now says read `git status` before the pull and the whole staged index (`git diff --cached`).
      Drift is now measured against `origin/main` after a fetch. Hand-check: 0 drift lines, three
      placeholder fills, no residual placeholders. `stampscan` still cannot pass a child (it cannot resolve
      the `source=` path from a child's root; atelier's open ST3). Cold pass queued at
      [`060/100`](100-cold-pass-owed-the-0a2b7a7-floor-restamp.md).
      review: queued — `060/100` (a retrofit of a stamped copy lands with its own pointer; RB12's counsel)
