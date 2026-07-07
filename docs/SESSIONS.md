# rpi-sdinfo session log (append-only)

One entry per working session, newest LAST. **Append only — never edit or rewrite prior entries.** At session
start read only the last few entries (e.g. `tail -80 docs/SESSIONS.md`); the full history is for grepping, not
for loading into context. This is ops memory, not product doc — the user-facing history is `CHANGELOG.md` and
the per-version detail is `docs/ROADMAP-DONE.md`.

Convention adopted 2026-07-08 from the sibling `ros`/`tiki` repo (lean roadmap + companions, ADRs, this log,
`why`-not-`what` comments, the `#!#` TODO marker, ruff in CI). The public/private doc split that `ros` uses is
*not* adopted here: rpi has no secrets or site-personal data, so everything stays in the one public tree.

---

- **2026-07-08**: Three feature chunks then a conventions adoption. (1) **macOS UX polish** — `gather_macos()`
  now auto-detects an inserted removable/external card when no `--device`/`--dir` is given (prefers an SD-bus
  reader, points the benchmark at its mount point, announces the pick) instead of silently profiling the boot
  disk; `macos_card_identity()` reads a built-in SD slot's real card product/make/serial from
  `system_profiler SPCardReaderDataType` to fill gaps `diskutil` leaves. New `tests/test_macos.py`. (2) **CSD
  structural liar-checks** in `cross_check()` — reserved structure version, zero/undefined TRAN_SPEED,
  empty/mandatory-missing command classes, illegal READ_BL_LEN (all `warn`; a malformed register is a
  counterfeit tell). Deliberately did NOT ship the TRAN_SPEED-vs-class fake inference (unsound — see below).
  (3) **Bus-ceiling `info` note** — a genuine high-class card on a slower bus is explained (bus-limited on a
  non-UHS host), on Mike's steer that the tool should show detail, not stay silent or cry fake. (4) **Adopted
  ros/tiki conventions**: split `ROADMAP.md` → lean roadmap + `docs/ROADMAP-DONE.md`; added `docs/SESSIONS.md`
  (this file), `docs/ARCHITECTURE.md`, `docs/decisions/` with ADRs 0001 (stdlib-only), 0002 (Apache-2.0),
  0003 (no fake-inference-from-TRAN_SPEED); added `ruff` (dev-only) with a CI lint job and fixed the 5 real
  issues it found (dead `import time`/`os`, unused `mid`/`device`, a lambda→def). Skipped mypy (untyped, 3.6
  floor) and the ARCHITECTURE-in-shipped-tree/private-doc split (N/A — no secrets). Commits: `6306f78`
  (macOS), `9224068` (CSD liar-checks), `599ed57` (bus-ceiling), + this conventions commit. 93 tests green;
  `ruff check .` clean. **Next**: still the standing v1.0 blocker (Pi hardware test); the cleanest
  testable-here item is the congruence-busting non-power-of-two capacity probes in `verify.py`.
