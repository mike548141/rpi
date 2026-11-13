# 2026-07-08 (cont.) — Congruence-busting decimal capacity probes

> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `d5c3c83`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-08 (cont.)**: Shipped the **congruence-busting decimal probes** flagged as next. `corner_offsets()`
  now, in addition to block 0 / the power-of-two offsets / the last block, probes each common decimal capacity
  boundary below the reported size (`COMMON_FAKE_CAPACITIES_BYTES` = 1/2/4/…/512/1000/2000 GB in *decimal*
  bytes). Rationale: a fake whose real chip wraps at a round decimal boundary has no power-of-two structure, so
  no power-of-two probe pair need be congruent mod R and the wrap slips past; probing the boundary C itself makes
  C alias onto physical 0 (`C mod C == 0`), overwriting block 0 → caught. Every n·10⁹ is a multiple of 512, so
  the exact-boundary probe stays block-aligned for raw-device I/O (documented in the comment). A *truly
  arbitrary* wrap can still evade both probe families — the free-space sweep remains the exhaustive backstop, so
  corners is explicitly a fast first-pass. Added 3 tests (boundary inclusion, 512-alignment invariant, and an
  end-to-end 8 GB-chip-reports-512 GB `FakeDevice` catch); 96 tests green. Docs synced: README corners bullet,
  ROADMAP item (now ✅ with the arbitrary-wrap caveat), CHANGELOG Unreleased. `ruff` not installed in this env so
  not run locally — CI will lint; the change is plain 2-space stdlib code with no new imports. Commit: pending.
  **Next**: still the v1.0 blocker (Pi hardware test). Other testable-here candidates: the ~116-function
  docstring conversion (documentation-as-code), or `read_file(return_scope='lines')` returning a line *range*.
