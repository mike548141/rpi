# 2026-07-12 — Atelier drift and pin bump, then a CID-database slice

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 33+1 -->
- [2026-07-12 · Atelier drift and pin bump, then a CID-database slice](2026-07-11-1335-pin-bump-cid-database.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `ddfdb1a`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-12** — **Atelier drift + pin bump, then a CID-database slice.** Start-of-session drift check
  surfaced 5 atelier commits past the pin; the only canonical-method change (`dfd5aec`) adds a RECORD.md rule
  that *public* records keep private siblings generic — it governs atelier's own records, not this private
  repo's, so nothing here needed scrubbing. Read the delta, bumped the pin `1588fda`→`9c63bfc` deliberately
  (`051263c`). Then Mike picked the CID-database thread and I shipped a three-part slice: **(#1)** extracted the
  251-line crowd-sourced `manufacturer` table out of `cli.py` into its own `src/rpi_sdinfo/cid_db.py` verbatim
  (provenance `# CID:` comments intact) so a contribution is a data diff, not code — plus a `validate_cid_db()`
  structural validator and a `leaf_capacity_bytes()` label parser (`8442d3d`; needed a `leakscan:allow` on the
  standard author-header line, which every source file carries). **(#2)** `tests/test_cid_db.py` — asserts the
  shipped table validates clean and proves the validator rejects each fault class (`6fac35d`). **(#3)** the
  **known-good fingerprint capacity cross-check**: when the full CID (MID/OID/PNM/PRV) exactly matches a verified
  product, its label states the capacity, so a card wearing that identity while reporting a grossly different
  size is flagged (`warn` past a 25% band, non-destructive) — `gather` stashes `storage['cid_db_match']`,
  `cross_check` compares (`446691d`). Explicitly **rejected the brand-vs-MID reverse index** as unsound (OEM/ODM
  rebadging → a genuine card legitimately carries another maker's MID; the DB's own Phison→Sony/Lexar/PNY entry
  proves it) — that was the real reason it was "deferred", not DB sparseness. Recorded as **ADR 0007** with docs
  synced (ROADMAP both CID items, CHANGELOG, README CONSISTENCY, CONTRIBUTING how-to) (`a2a9231`). 138 tests
  green throughout; all pre-commit floor scanners clean. **Nothing pushed** — 6 local commits on `main` since
  last sync (`051263c`→`a2a9231`). **Next**: unchanged big rocks — the v1.0 Pi-hardware blocker (only testable
  on hardware) and the Mike-gated decisions (crowd-upload anonymisation scheme, tag `v0.9.1`, PyPI-or-not). The
  CID DB is now structured to *grow* — but growing it needs real observed cards, never invented mappings.
