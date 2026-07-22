# 0008 — Anonymisation scheme for the (future) crowd-sourced upload

**Status**: Proposed — awaiting Mike's ruling • **Date**: 2026-07-22

> This decision is the principal's to make. The ADR exists to make that ruling an *informed* one:
> it lays out the threat model, classifies every field by research-value-vs-identifying, weighs the
> options honestly, and recommends one scheme — but **nothing here ships, and no upload code is
> written, until Mike rules on what is safe to share** (see [Gated on Mike](#gated-on-mike)).

## Context

The roadmap carries a *future, optional* feature: a POST of a test result to a shared database so the
community can pool `CID → real product + measured performance + failure rate` data. That data makes
fake-detection stronger (it feeds the CID database and the ADR 0007 fingerprint cross-check). The
roadmap flagged that the current anonymisation is too weak to reuse for upload. This ADR settles what
an upload may safely contain, before any endpoint or upload code exists.

### What ships today (so the analysis is grounded)

The **local** SQLite path (`--save-db`, `cli.py`) is the only thing that touches these fields today, and
it is **local-only** — no network, no anonymisation obligation. For the record of exactly what exists:

- `host_uuid` = `pbkdf2_hmac('sha256', serial, b'rpi-sdinfo/device-uuid/v1', 1000).hex()` where `serial`
  is the **Raspberry Pi's host serial** (from `/sys/firmware/devicetree/base/serial-number`) — **not the
  card's serial**. Fixed public salt, 1000 iterations.
- The **card serial** (`cid_psn`, the 32-bit PSN) is stored **in the clear** as its own column.
- The **full CID** register, the Pi's MACs, and everything else are stored verbatim in the `document`
  JSON blob.

This is fine locally. It is emphatically **not** an upload scheme, and the roadmap's shorthand ("fixed-salt
PBKDF2 over the serial") is imprecise in a way that matters: the PBKDF2 protects the *host* serial, while
the *card* serial that an upload would key on is not hashed at all. Neither the KDF nor its salt is doing
any anonymisation work for the card. **An upload cannot be a subset of the local row — it needs a
purpose-built payload.**

### Threat model

**What a naïve upload record would contain:** the full CID (MID/OID/PNM/PRV/PSN/MDT/CRC), CSD fields,
reported capacity, measured performance (seq write, random read/write IOPS), and the verdicts
(grade/capacity/consistency/overall). Possibly the `host_uuid` and, if the whole `document` were shipped,
the Pi's MACs and host serial.

**The two hard identity facts:**

1. **A full CID uniquely identifies one physical card.** It is 128 bits and includes a 32-bit serial plus
   manufacture date; the tuple is globally unique per card by design. Uploading the full CID *is*
   uploading a permanent, unique fingerprint of that specific piece of hardware.
2. **The card serial (PSN) is only 32 bits** — 4.29 × 10⁹ possible values. Any hash over it with a
   **public** salt is not anonymisation, it is obfuscation:
   - Plain SHA-256, public salt: the entire 2³² keyspace can be enumerated (or a full lookup table
     precomputed) in **well under a second** on commodity GPU hardware.
   - Even the shipped **PBKDF2-HMAC-SHA256 at 1000 iterations**: ~4.3 × 10¹² hash-ops to exhaust 2³²
     candidates, which a single high-end GPU clears in **minutes to about an hour**, and a small rig in
     minutes. 1000 iterations was never sized to defend a 32-bit secret.
   - And it is **moot anyway**: if the full CID is uploaded (as the roadmap wording implies), the PSN is
     right there in the clear inside it. Hashing the PSN while shipping the CID protects nothing.

**Linkage risks:**

- **Across uploads:** a stable per-card token (or the CID itself) lets anyone with the published dump group
  every upload of the same physical card, and a stable *host* token groups every card one person tested —
  reconstructing a hobbyist's fleet and testing timeline.
- **Against the local history:** the local `--save-db` file keeps the real serials and MACs. If an upload
  reused the same `host_uuid` derivation, a dump + a copy of someone's local DB (or their known Pi serial)
  links published records straight back to the machine and its owner.

**Who the adversary realistically is, and the harm (kept proportionate):** this is a hobbyist card
database, not a bank. The realistic adversary is someone who obtains the *public* dataset and wants to
correlate records — a curious peer, a data scraper, at most a griefer. The harm is a **privacy/linkage
nuisance**: deanonymising which cards a person owns, tying a batch of uploads to one machine via a
hardware-derived ID or MAC, and (weakly) location/purchase inference from manufacture dates and timing.
There is no credible high-stakes attacker here and this ADR will not pretend otherwise — **but the correct
fix costs almost nothing, so there is no reason to ship a leaky one.** The bar is "publish nothing that is a
unique physical-card fingerprint or a hardware-derived tracker," not "defend against a state actor."

### First, why would an upload want a card identifier at all?

"Drop the serial" is only assessable against the goals an identifier would serve. Two are plausible:

1. **Dedup of resubmissions** — stop one enthusiast who tests the same card 50 times from skewing the
   failure-rate statistics for that model.
2. **Fleet / spam control** — rate-limit or throttle a single source flooding the endpoint.

Neither actually needs a per-*card* identity. The **research value is per-*model* aggregate** (this model,
at this capacity, performs like *this* and fails at *this* rate) — that is computed by grouping on the
non-identifying model class, not on unique cards. Dedup (1) is served well enough by down-weighting at
*install* granularity; spam control (2) is an *install/source* concern, not a card concern. So the honest
finding is: **the aggregate goal does not require a unique card identifier, and the two operational goals
are met by an install-level token, not a card-level one.**

### What has research value vs what is identifying

| Field | Research value | Identifying? | Classification |
|---|---|---|---|
| MID (manufacturer id) | High — the maker | Low alone (shared by millions) | **Safe** |
| OID (OEM id) | High — the brand line | Low alone | **Safe** |
| PNM (product name) | High — the product | Low alone | **Safe** |
| PRV (product revision) | Useful — silicon rev | Low alone | **Safe** |
| Reported capacity | High — core to fake-detection | Low alone | **Safe** |
| CSD fields (class, tran_speed, block len, capacity type) | High — the whole point | Low alone | **Safe** |
| Measured performance (seq/rand IOPS) | High — real-world data | Low alone | **Safe** (coarsen/bin to be safe) |
| Verdicts (grade/capacity/consistency/overall) | High — failure rates | Low alone | **Safe** |
| Manufacture date (MDT) | Useful — cohort/aging analysis | Medium — narrows a card, aids linkage | **Useful-but-identifying** → coarsen to year |
| **PSN (card serial)** | **~None** — a random per-unit number carries no product signal | **High** — the per-unit identifier | **No value + identifying → drop** |
| **Full CID** (as a unit) | Its *fields* have value individually | **High** — unique card fingerprint (contains PSN) | **Don't ship as a unit; ship the fields, not the register** |
| Pi host serial / `host_uuid` | None | High — identifies the uploader's machine | **No value + identifying → never upload** |
| MAC addresses | None | High — identifies the machine/NIC | **No value + identifying → never upload** |

The key structural insight: **every field with research value is a per-*model* attribute and is safe;
every field that uniquely identifies the *card* or the *uploader* carries no research value.** They come
apart cleanly, which is what makes a safe scheme cheap.

## Decision (recommended — for Mike to accept or amend)

**Recommend Option A + Option D, and explicitly not shipping the full CID or any host identifier.**

Concretely, an upload payload should be **built field-by-field, not derived from the local row**, and contain:

- **Model class, in the clear:** MID, OID, PNM, PRV, reported capacity, and the non-serial CSD fields.
  These are shared by millions of cards and are exactly the research signal.
- **Performance and verdicts**, optionally binned (e.g. IOPS to sensible buckets) so a fingerprintable
  exact-measurement tuple can't itself become an identifier.
- **Manufacture date coarsened to the year** (Option-D-adjacent hygiene).
- **A resettable, random per-install ID** (`uuid.uuid4()`, generated once, stored in `~/.rpi-sdinfo/`,
  documented and user-resettable) — sent *only* for server-side rate-limiting/spam control and
  install-granularity dedup. It is **not derived from any hardware ID**, so it re-identifies neither the
  card nor the machine, and the user can wipe it at will.

And it must **NOT** contain: the PSN, the full CID register as a unit, the Pi host serial, `host_uuid`, or
any MAC.

**Why this scheme, sized to this project:**

- It needs **no server secret and no KDF** — there is no pepper to leak and no iteration count to argue
  about, because nothing card-unique is uploaded to protect. That suits a project that is **stdlib-only,
  zero-dependency, and has no server yet.** `uuid.uuid4()` is stdlib.
- It is **honest**: nothing uploaded is a unique physical-card fingerprint or a hardware-derived tracker,
  so the tool can truthfully tell a user what leaves their machine.
- It **preserves the actual goal** (per-model aggregate performance/failure data) fully, and meets the two
  operational goals (dedup, spam control) at install granularity — the granularity they actually need.
- The only thing it sacrifices is **per-card dedup**, which the aggregate goal does not require. If per-card
  dedup ever proves genuinely necessary, revisit toward Option B (HMAC-pepper) — but only **once a server
  that can hold a secret actually exists**; don't build secret-holding infrastructure for a need the goal
  doesn't have.

Upload must also be **strictly opt-in per run**, and the tool should be able to **show the exact payload**
before sending it.

## Rejected (and the options weighed)

- **(B) HMAC(card serial or CID) with a server-held pepper.** *Pros:* brute-force-infeasible without the
  pepper; yields a stable per-card token, so the server can dedup and rate-limit precisely. *Cons:* requires
  a **server that holds a secret** — none exists, and standing one up is spend + a new trust surface (floor
  actions). The client can't compute the token itself, so either it ships the raw serial for the server to
  HMAC (the server transiently sees real serials — a trust ask) or it can't participate. If the pepper ever
  leaks, every record collapses back to the 2³² brute-force. **Deferred, not dead:** this is the right answer
  *if and only if* Mike rules that per-card dedup is a hard requirement and a real server exists.
- **(C) Truncated hash / k-anonymity binning of the serial.** *Pros:* no server secret; provable
  k-anonymity — truncating the hash forces many cards into each bucket. *Cons:* it only gives **soft/collision
  dedup**, not reliable per-card identity, and it still ships a function of a 2³² input; tuning `k` is fiddle
  for a benefit (per-card dedup) we've already found we don't need. Binning is still worth doing on
  *performance* fields (adopted above) — but as anti-fingerprinting, not as a serial scheme.
- **(E) Keep PBKDF2 but use a per-upload random salt.** **Rejected outright — worst of both worlds.** A random
  salt makes the same card hash differently every upload, so it **destroys the dedup goal entirely**, *and*
  the salt must travel with the record for verification, leaving each individual record's 2³² input
  brute-forceable on its own. No privacy gained, dedup lost. Named only to close it off explicitly.
- **Shipping the full CID in the clear (the roadmap's literal wording).** Rejected: the CID is a unique
  physical-card fingerprint and contains the PSN, so it defeats any serial-hashing entirely. Ship the CID's
  *research-bearing fields* individually instead — never the register as a unit.

### Prior art (verified July 2026)

- **smartmontools `drivedb.h`** stores **model-family and firmware regexes**, not per-unit serials — it is a
  curated identification table maintained by manual pull requests, so the published database holds **no device
  serial numbers**; a contributor's serial appears only transiently in a submission ticket, never in the shipped
  data. That mirrors the recommendation here: publish the *model class*, not the *unit*.
  ([drivedb.h](https://github.com/smartmontools/smartmontools/blob/master/smartmontools/drivedb.h))
- **f3 (Fight Flash Fraud)** has **no upload and no central database at all** — `f3write`/`f3read`/`f3probe`
  are purely local write/verify tools. So the closest sibling project simply sidesteps the question by never
  collecting anything. ([f3 docs](https://fight-flash-fraud.readthedocs.io/), [AltraMayor/f3](https://github.com/AltraMayor/f3))

*(Both verified by search on 2026-07-22; I did not find a documented smartmontools policy statement on serial
handling, so the claim above is limited to what the shipped `drivedb.h` format demonstrably contains.)*

## Consequences

- The community database becomes a set of **per-model records** — exactly what feeds the CID database and the
  ADR 0007 fingerprint cross-check — with **nothing published that fingerprints a specific card or its owner's
  machine.** The tool can make an honest, checkable promise about what leaves the device.
- **Per-card dedup is given up** by design. Failure-rate stats are down-weighted at install granularity, not
  per physical card; if a heavy re-tester ever distorts the data enough to matter, that is the trigger to
  revisit Option B — with a real server and a fresh spend/trust ruling, not before.
- Any upload feature must still carry **strict opt-in and a "show me exactly what you'll send" affordance**;
  those are non-negotiable regardless of which scheme lands.
- This ADR governs the **upload path only**. The **local `--save-db`** behaviour is unchanged and out of scope:
  it stays local-only and keeps real identifiers, which is correct for a private on-disk history.

## Gated on Mike

The following are explicitly the principal's calls; no upload code should be written until they are answered:

1. **The "safe to share" ruling itself** — is the recommended field set (model class + coarsened MDT + binned
   perf + verdicts + resettable install ID, and *nothing* card-unique or host-derived) acceptable to publish?
2. **Is per-card dedup a real requirement?** If yes, the scheme changes toward Option B (HMAC-pepper) and a
   server that holds a secret — which is a different, heavier design.
3. **Any spend** on an endpoint (S3 bucket / API / hosting) — a floor action (spending money), and a new trust
   surface if it holds a pepper or accepts writes.
4. **Confirmation that no upload feature ships before this ruling** — the roadmap marker and this ADR both
   stand until Mike converts Status to accepted/amended.
5. **Consent model** — is opt-in-per-run + payload preview the required UX, or stricter?
