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
