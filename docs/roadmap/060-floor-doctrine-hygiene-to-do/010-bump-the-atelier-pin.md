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
    - **2026-11-13**: `0a2b7a7` → `2a6d7a4` — 340 atelier commits. Done by a headless
      Opus 5.5 session dispatched by an estate health sweep (orchestrator session
      `e820bff5`). **Read in full:** the `docs/method/PROPAGATION.md` diff
      `0a2b7a7..2a6d7a4` (820 lines), which holds the `floor` region. **Taken from a
      digest, not read line by line:** the rest of the `docs/method` and template
      delta, summarised by a read-only research session that read every hunk of it.
      The floor is re-stamped word for word from the region at `2a6d7a4`, with the
      same four fills. What moved in it: bulk deletion from a record store is now a
      confirm stop; the informed confirmation is "the full account `00-APEX.md`
      owes"; the *Asking* bullet adds the no-device case and "any other
      consideration"; *Concurrency* opens with `cclive` and says "where the branch
      has an upstream"; *Doctrine problems point up* says class only; the drift check
      is now `fetch -q && … log` (a fetch error is no result); *Estate resources*
      drops "never by name" for "named, contents by type only". **Verified:**
      `pins.py --child` reads `current` and `✓ identical`. `pins.py` now does the
      comparison this item used to do by hand, which bears on `060/100`'s FS1.
      Beneath the block, the session-log read step gains the cold-reviewer clause
      (REVIEW.md rule 2). No `Pending upstream:` lines exist to sweep. No cold pass
      is queued for this re-stamp: the question the last one asked first (is the copy
      word for word?) is now answered by a tool, and whether a verbatim re-stamp
      still earns a Fable pass is put to the principal in the sweep's report rather
      than decided here.
