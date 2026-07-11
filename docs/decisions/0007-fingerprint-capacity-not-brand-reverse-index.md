# 0007 — CID fake-detection compares against a verified fingerprint, not a brand-vs-MID reverse index

**Status**: accepted • **Date**: 2026-07-12

## Context

The CID database maps a card's registers to a make/brand/product. A tempting next fake-detection check is a
**brand-vs-MID reverse index**: the MID is assigned by SD-3C to a specific manufacturer, so if a card's branding
claims make *B* while its MID is registered to make *A*, call the mismatch a counterfeit tell. The roadmap
carried this idea ("MID that never ships the branded make") as deferred-until-the-DB-is-richer.

On inspection the idea is unsound, and DB sparseness was never the real blocker. **The database itself refutes
it.** Entry `0x000027` is Phison, whose OEM line reads *"AgfaPhoto, Delkin, Integral, Lexar, Patriot, PNY,
Polaroid, Sony, or Verbatim."* A **genuine** Sony or Lexar card legitimately carries Phison's MID — OEM/ODM
rebadging (a brand selling another maker's silicon) is normal and pervasive in the SD world. So "MID-maker ≠
brand" is routinely true on honest cards. Firing "fake" on it would mislabel good hardware and violate
[ADR 0004](0004-honest-diagnostic-not-a-pass-fail-toy.md)'s rule: never cry fake on an inference a genuine card
could legitimately trip (the sibling of [ADR 0003](0003-tran-speed-is-not-proof-of-fake.md)).

There *is* a sound check hiding nearby. When the **full** CID (MID/OID/PNM/PRV) exactly matches a *verified*
product entry, we are no longer inferring a maker from an ambiguous field — we hold a known-good fingerprint,
and that product's own label states its capacity.

## Decision

Ship the **known-good fingerprint capacity cross-check** and reject the brand-vs-MID reverse index.

When the full CID matches a verified DB leaf and that leaf's label states a capacity, compare it to the size the
card reports. A card wearing that exact identity while reporting a grossly different capacity is a strong
counterfeit tell — a clone that copied a real card's registers but was flashed to lie about size — and it needs
no destructive write to see. The check:

- fires **only on an exact fingerprint match** (`storage['cid_db_match']`), never on a make/OEM fallback;
- derives the expected size from the leaf's **own label** (single source of truth — no separate, drift-prone
  capacity field), and stays silent if the label states no parseable GB size;
- uses a **loose 25% band**, tolerating genuine marketing-GB-vs-usable-bytes slack and catching only gross (2×+)
  lies — the corners / free-space sweep remains the backstop for subtle wraps;
- is **`warn`, never `fail`**: the DB entry could itself be wrong, so this is a strong hint, not a spec-impossible
  certainty.

## Rejected

- **Brand/make vs MID reverse index.** Rejected as unsound: OEM/ODM rebadging means a genuine card legitimately
  carries another maker's MID, so the mismatch is not a fake signal. The DB's own Phison→(Sony/Lexar/PNY/…) OEM
  entry is the counter-example. This is an ADR 0004 violation waiting to happen, not merely a sparse-data
  problem.
- **A `fail` severity for the capacity mismatch.** Rejected: unlike the Standard-Capacity-CSD-claims->4GB check
  (physically impossible per the spec), a fingerprint-vs-capacity disagreement rests on a crowd-sourced DB entry
  that could be wrong. Honesty caps it at `warn`.
- **Storing a machine-readable `capacity_bytes` on every leaf.** Rejected for the existing entries: it duplicates
  a fact already in the label and can drift out of sync. The label is parsed at check time instead. (The field is
  *permitted* — the validator checks it against the label when present — for a future entry whose label is
  genuinely ambiguous.)

## Consequences

- Fake-detection gains a non-destructive capacity check that is **sound every time it fires**, and grows in reach
  as the CID database grows — the database becomes an active detector, not just a labeller.
- The check fires rarely today (few verified fingerprints in the table), and that is honest: it speaks only when
  it has ground truth. Growing the crowd-sourced DB is what strengthens it — with real observed CIDs, never
  invented mappings (an invented entry would poison detection).
- A contributor tempted to re-raise "flag brand≠MID" should read this ADR first: the answer is no, and the reason
  is OEM rebadging, not a thin table.

## Addendum (2026-07-12) — reject the *binary* reverse index, not the signal

*Mike's steer, same day: the decision above over-corrected. "Reject the reverse index" was too broad — what is
unsound is the **binary** form (brand≠MID ⇒ fake), not the brand↔MID relationship itself, which is real,
learnable data. The rejection stands only for the binary trigger; the relationship is adopted in scored form.*

- **Learn the brand set, don't assume it.** The unsoundness came from *assuming* a MID ships only its maker's
  own brand. The fix is to *learn*, per MID (and per OID), the set of brands legitimately observed shipping under
  it — the free-text OEM string (`'AgfaPhoto, Delkin, … Sony'`) becomes structured, countable data that grows
  with every real card. A well-populated pairing then nudges toward genuine; a pairing never seen under a
  heavily-observed maker nudges toward suspect.
- **A score, never a verdict.** The signal feeds a **heuristic suspicion score**, not a fake/genuine flag. This
  is fully consistent with [ADR 0004](0004-honest-diagnostic-not-a-pass-fail-toy.md): soft signals aggregate into
  an *explained* score (always shown with its contributing reasons, never a bare light/number), while only
  spec-impossible facts remain hard `fail`s that drive the exit code. Absence of evidence is not evidence — an
  unknown pairing pulls near-neutral until the maker is well-observed, so a genuine oddball card is not punished
  for a thin table.
- **Honesty bound:** it is a *suspicion index*, not a calibrated P(fake). With no labelled ground-truth we must
  not print a probability ("73% fake" claims more than the evidence bears); the honest artefact is a heuristic
  score with named signals underneath it.

The scoring model itself (weights, thresholds, where a "sold-as" brand beyond the OID comes from, whether the
score ever influences the exit code) is a larger design carried in the roadmap and will earn its own ADR when
built. This addendum only records that the brand↔MID signal is **kept, in learned + scored form** — the earlier
blanket "rejected" is narrowed to the binary trigger.
