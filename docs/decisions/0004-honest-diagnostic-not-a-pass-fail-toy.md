# 0004 — rpi-sdinfo is an honest diagnostic instrument, not a pass/fail toy

**Status**: accepted • **Date**: 2026-07-08

## Context

It is tempting to build a card checker as a consumer appliance: one big green GENUINE / red FAKE light, every
nuance hidden so a novice can't misread it. That framing quietly narrows the tool to a single question ("real or
counterfeit?") and trains it to collapse every cause into that one axis.

But the tool's actual purpose is broader than counterfeit-catching. A card can be:

- **genuine but faulty** — real silicon, failing or worn cells, high-latency tail;
- **genuine but bus-limited** — a real U3/V30/A2 card measuring slow because the *host, reader, slot or bus* is
  the bottleneck, not the card (the canonical case: a genuine UHS card on a ~25 MB/s non-UHS reader; see
  [ADR 0003](0003-tran-speed-is-not-proof-of-fake.md));
- **genuine but generally slow** — an honest low-class card performing exactly to its (modest) rating;
- **an outright counterfeit** — capacity fraud or a spec-impossible register.

These are different diagnoses with different fixes. Flattening them into fake/genuine throws away most of the
tool's value and, worse, mislabels good hardware.

And the audience is not a luddite. **The fact that someone is running a CLI card diagnostic at all means they
can read a nuanced answer.** They are diagnosing something — a flaky Pi, a slow copy, a suspect marketplace buy
— and they deserve to be told what is actually happening, not shielded from it.

## Decision

**Report what is actually happening, honestly, and name the likely cause.** The tool separates its axes —
identity/counterfeit, measured performance, and register/health consistency — and each is reported on its own
terms rather than merged into one verdict. When a genuine card underperforms, say *why* (bus/host ceiling, wear,
honest low rating) instead of either failing it or silently calling it fine. When something is a spec-impossible
counterfeit tell, say so plainly.

Concretely this means: prefer an explanatory `info`/`warn` with the real cause over a blunt pass/fail; never
dumb a finding down for fear the user can't handle it; and never cry "fake" on an inference that a genuine card
could legitimately trip (ADR 0003 is the worked example of that rule).

## Rejected

- **A single fake/genuine light with the detail hidden.** Rejected: it discards the general-performance and
  fault-diagnosis half of the tool's purpose, and it mislabels genuine-but-slow or genuine-but-bus-limited cards
  as suspect. The audience is capable; treat them as diagnosticians.
- **Staying silent to look clean.** Rejected on Mike's steer: a real card measuring below its label deserves an
  explanation, not a bare green tick that leaves the user guessing.

## Consequences

- Output stays sectioned (identity · grade · capacity · consistency) so causes don't bleed into one verdict.
- Findings carry a severity (`info`/`warn`/`fail`) that maps to *how sure and how serious*, not just "bad".
- The exit code reflects only sound, spec-grounded failures; explanatory nuance rides in `info`/`warn` and never
  poisons the code (again, ADR 0003).
- A contributor adding a check should ask "what is the honest diagnosis, and its real cause?" — not "does this
  make the fake/genuine light redder?".
