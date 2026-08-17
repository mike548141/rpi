- [ ] **CID/CSD cross-checks.** ✅ Shipped in 0.7 (`cross_check()`): flags a Standard-Capacity CSD claiming a
      high/extended capacity (impossible), a CSD-vs-reported capacity mismatch, and a future manufacturing date.
      ✅ Extended (post-0.9): **structural-validity liar-checks** on the register itself — reserved CSD structure
      version (3), a zero/undefined TRAN_SPEED, empty or missing-mandatory command classes (basic/read/write), and
      an illegal READ_BL_LEN. A genuine controller emits a spec-valid register, so garbage here is a counterfeit
      tell (all `warn` severity — strong hints, not exit-code fails).
      - **Rated class vs TRAN_SPEED — surfaced as `info`, never as a fail.** Inferring "this card can't be A2/U3"
        from a low TRAN_SPEED is *unsound*: UHS bus speed is negotiated out-of-band (CMD6/CMD11), so a genuine UHS
        card legitimately still reports 25/50 Mbit/s in the legacy field. Failing on it would poison credibility.
        Instead, when the rated class exceeds what the advertised bus can carry (e.g. a U3/V30 card on a high-speed
        ~25 MB/s bus), the tool emits an **info** note explaining the ceiling — so a genuine card measuring below
        its label is understood (bus-limited on a non-UHS host), not silently believed fast or assumed broken.
      - **Known-good fingerprint capacity cross-check.** ✅ Shipped (post-0.9.1): when the full CID
        (MID/OID/PNM/PRV) exactly matches a *verified* product in the database, that product's label states its
        capacity, so a card wearing that exact identity while reporting a grossly different size is flagged (`warn`
        past a 25% band; a clone flashed to lie about capacity, caught with no destructive write). Fires rarely today
        but is sound every time it does, and strengthens as the DB grows.
      - **Brand↔MID as a learned, *scored* signal (not a binary tell).** The naive "brand≠MID ⇒ fake" trigger is
        unsound (OEM/ODM rebadging — the DB's own Phison→Sony/Lexar/PNY entry proves a genuine card carries another
        maker's MID). But the brand↔MID *relationship* is real, learnable data: structure the free-text OEM string
        into a countable **set of brands observed shipping under each MID/OID**, growing with every real card, and let
        a well-populated pairing nudge toward genuine / a never-seen pairing nudge toward suspect. Feeds a **heuristic
        suspicion score**, never a verdict.
        ✅ **First slice shipped:** the structured brand-set data model (`brand_sets()` / `brands_observed()` +
        `validate_brand_sets()` in `cid_db.py`, derived live from the make/OEM fields so it grows with the table) and a
        neutral `info` finding in `cross_check()` that surfaces the observed brand set for a human to compare against
        the card's physical label — never a verdict, silent on an unseen/thin pairing (unknown ≠ suspicious), no score
        and no exit-code effect. ◑ **Still to come (own ADR):** the aggregate suspicion score itself. Design
        constraints (from [ADR 0007 addendum](../../../docs/decisions/0007-fingerprint-capacity-not-brand-reverse-index.md)):
        - **Hybrid, so [ADR 0004](../../../docs/decisions/0004-honest-diagnostic-not-a-pass-fail-toy.md) holds** — spec-impossible facts stay hard `fail`s that drive the
          exit code; soft signals (brand-set, capacity-vs-fingerprint, register oddities, date, TRAN_speed context)
          aggregate into a *separate, explained* score, always shown with its contributing reasons, never a bare light.
        - **Suspicion index, not P(fake)** — no labelled ground truth to calibrate a probability, so never print a
          percentage; a heuristic score with named signals is the honest artefact.
        - **Unknown ≠ suspicious early** — an unseen pairing pulls near-neutral until the maker is well-observed, so a
          genuine oddball isn't punished for a thin table.
        - Build incrementally: first the structured brand-set data model + a neutral "consistent with known brands for
          this maker" **info** finding (zero risk, starts accumulating value); the aggregate score comes later, once
          the table is rich enough for weights to mean anything, and earns its own ADR then.
