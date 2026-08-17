- [ ] **Grow the CID database.** The MID/OID → product table is crowd-sourced and incomplete; every verified
      `CID → real product + measured performance` mapping makes fake-detection stronger. ✅ The table now lives in
      its own file (`src/rpi_sdinfo/cid_db.py`) so a contribution is a data diff, not a code change, gated by a
      structural validator (`validate_cid_db`) the suite runs on every change. Still just needs *more real cards* —
      each verified fingerprint also arms the capacity cross-check above.
