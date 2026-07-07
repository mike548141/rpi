# 0003 — A fake is never inferred from the CSD TRAN_SPEED field

**Status**: accepted • **Date**: 2026-07-08

## Context

The CSD register carries a `TRAN_SPEED` field (decoded by `decode_csd()`). An early roadmap idea was to treat a
low TRAN_SPEED against a high rated class as a counterfeit signal — e.g. "an A2/U3 label on a card whose CSD
only advertises 25 Mbit/s must be lying." It is an appealing check: instant, non-destructive, metadata-only.

It is also **unsound**. UHS bus speeds (SDR50/SDR104, and even High-Speed mode) are negotiated *out of band*
from `TRAN_SPEED`, via the CMD6 function switch and CMD11 voltage switch — not by updating this legacy field. A
genuine UHS-I card therefore commonly still reports 25 or 50 Mbit/s in `TRAN_SPEED`. Inferring incapability from
it would flag real SanDisk Extreme / Samsung EVO-class cards as suspect.

The tool's entire value rests on its verdicts being trustworthy. A fake-detector that cries wolf on genuine
cards is worse than one that stays quiet: it trains users to ignore it, and it slanders good hardware.

## Decision

**Never emit a `warn`/`fail` fake finding derived from TRAN_SPEED-vs-class.** Instead, when a card's rated class
needs more sustained write than its advertised bus can carry (e.g. a U3/V30 card on a ~25 MB/s high-speed bus),
`cross_check()` emits an **`info`** note explaining that UHS speed is negotiated separately and the card is
bus-limited on a non-UHS host/reader/slot. This makes the nuance *visible* (a genuine card measuring below its
label is explained, not silently believed fast) without ever failing a real card.

This is separate from — and must not be confused with — the CSD **structural** liar-checks (reserved structure
version, zero/undefined TRAN_SPEED, empty/mandatory-missing command classes, illegal READ_BL_LEN), which flag a
register that is *malformed per the spec*. Those are sound: a genuine controller emits a spec-valid register.

## Rejected

- **Flag low TRAN_SPEED + high class as a fake (`warn`/`fail`).** Unsound for the out-of-band reason above;
  false-positives genuine UHS cards and poisons credibility.
- **Stay silent entirely.** Rejected on Mike's steer (2026-07-08): the tool should not be shy of showing detail.
  A user scanning a real U3 card that measures 22 MB/s deserves to know *why*, not just a green "genuine".

## Consequences

- The gap is surfaced as `info` only; it never touches the exit code.
- The `_CLASS_WRITE_MBPS` table + `_rated_write_floor()` encode the per-class sustained-write floors; the bus
  ceiling is `TRAN_SPEED_clock × 4 lines ÷ 8 bits` (25 Mbit/s → ~12.5 MB/s, 50 Mbit/s → ~25 MB/s), matching the
  bus table in [`SD_CARDS.md`](../../SD_CARDS.md).
- A future contributor tempted to "add the obvious TRAN_SPEED fake check" should read this first — the check is
  intentionally absent, not overlooked.
