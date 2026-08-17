- [ ] 🎯 **Crowd-sourced upload.** 🎯 *Design done (2026-07-22), Mike's ruling owed — ADR 0008 asks five questions
      (field set, per-card dedup?, endpoint spend, ship gate, consent model); no upload code before it.*
      Optional POST to an API / S3 bucket so results (CID, CSD, capacity, measured
      performance, pass/fail) build a shared database of card identifiers and real-world failure rates. Needs a
      purpose-built anonymisation scheme, not a subset of the local row: the card serial (PSN) is only 32 bits, so
      any public-salt hash over it is brute-forceable, and shipping the full CID uploads a unique per-card
      fingerprint outright (the local fixed-salt PBKDF2 hashes the *Pi host* serial, not the card, and does no
      upload-anonymisation work). Draft design + threat model + recommendation:
      [docs/decisions/0008-crowd-upload-anonymisation.md](../../../docs/decisions/0008-crowd-upload-anonymisation.md)
      (Proposed — awaiting Mike's ruling on what is safe to share; no upload ships before it).
