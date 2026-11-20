# rpi-sdinfo session log (append-only)

One entry per working session, newest LAST. **Append only — never edit or rewrite prior entries.** At session
start read only the last few entries (e.g. `tail -80 docs/SESSIONS.md`); the full history is for grepping, not
for loading into context. This is ops memory, not product doc — the user-facing history is `CHANGELOG.md` and
the per-version detail is `docs/ROADMAP-DONE.md`.

Convention adopted 2026-07-08 from the sibling `ros`/`tiki` repo (lean roadmap + companions, ADRs, this log,
`why`-not-`what` comments, the `#!#` TODO marker, ruff in CI). The public/private doc split that `ros` uses is
*not* adopted here: rpi has no secrets or site-personal data, so everything stays in the one public tree.

Since 2026-11-13 this file is an index: one line per session, newest last, each
pointing at the session's detail file in `docs/sessions/`. The entries written
here before then moved word for word into one detail file each; the line for
each keeps its entry's own date label. Append a one-line pointer here and put
the detail in `docs/sessions/YYYY-MM-DD-HHMM-slug.md` (`HHMM` in UTC).

<!-- indexscan:maps dir=sessions match=*.md -->

---

- [2026-07-08 · macOS UX polish, CSD liar-checks, bus-ceiling note, conventions adopted](sessions/2026-07-07-1605-macos-csd-checks-conventions.md)
- [2026-07-08 (cont.) · Congruence-busting decimal capacity probes](sessions/2026-07-07-1655-decimal-capacity-probes.md)
- [2026-07-08 (cont. 2) · Docstring conversion](sessions/2026-07-07-1717-docstring-conversion.md)
- [2026-07-08 (cont. 3) · ADR 0004: an honest diagnostic, not a pass/fail toy](sessions/2026-07-07-1726-adr-0004-honest-diagnostic.md)
- [2026-07-08 (cont. 4) · SBOM generator](sessions/2026-07-07-1732-sbom-generator.md)
- [2026-07-08 (cont. 5) · Release plumbing for v0.9.0](sessions/2026-07-07-1739-release-plumbing-v0-9-0.md)
- [2026-07-08 (cont. 6) · Artefact signing added to the roadmap](sessions/2026-07-07-1742-signing-roadmap-item.md)
- [2026-07-08 (cont. 7) · Release-readiness cleanup](sessions/2026-07-07-1815-release-readiness-cleanup.md)
- [2026-07-08 (cont. 8) · Artefact signing shipped](sessions/2026-07-07-1825-signing-shipped.md)
- [2026-07-09 · Queue build: `--block-sweep` shipped](sessions/2026-07-08-1334-block-size-sweep.md)
- [2026-07-11 · Adopted into the atelier fleet](sessions/2026-07-11-0656-adopted-into-atelier.md)
- [2026-07-12 · Atelier drift and pin bump, then a CID-database slice](sessions/2026-07-11-1335-pin-bump-cid-database.md)
- [2026-07-22 · First orchestrated queue run](sessions/2026-07-22-1036-first-queue-run.md)
- [2026-07-29 · Publish-safety review: cleared as the pilot](sessions/2026-07-29-1104-publish-safety-review.md)
- [2026-07-29 (cont.) · CI red to green, then the flip to public](sessions/2026-07-29-1129-ci-green-then-public.md)
- [2026-07-30 · Cold post-flip review and guardrails audit](sessions/2026-07-29-1203-post-flip-cold-review.md)
- [2026-07-30 (cont.) · Flaky CI test pinned and fixed](sessions/2026-07-29-1207-flaky-ci-test-fixed.md)
- [2026-07-30 (cont.) · Atelier pin `9e7e031` → `e45549a`](sessions/2026-07-29-1238-pin-bump-e45549a.md)
- [2026-07-30 (cont.) · Correction to the pin-bump entry](sessions/2026-07-29-1239-pin-bump-correction.md)
- [2026-07-30 (cont.) · The cold review written up as a review record](sessions/2026-07-29-1255-cold-review-record.md)
- [2026-08-17 · The board split: one file per item, generated index](sessions/2026-08-17-0555-board-split.md)
- [2026-08-17 (cont.) · The pin moved twice](sessions/2026-08-17-0952-pin-moved-twice.md)
- [2026-10-04 · The board-split cold-pass brief](sessions/2026-10-03-1153-board-split-brief.md)
- [2026-10-18 · Board-split cold pass ran and closed, with findings (`060/070`)](sessions/2026-10-17-2121-board-split-cold-pass.md)
- [2026-10-26 · Doctrine catch-up: pin `0af3006` → `0a2b7a7`](sessions/2026-10-26-1013-doctrine-catch-up.md)
- [2026-10-27 · The pin-bump questions answered and applied](sessions/2026-10-26-1229-pin-bump-answers.md)
- [2026-10-27 (cont.) · Line width: 85 columns for new writing, history exempt](sessions/2026-10-26-2342-line-width-85-columns.md)
- [2026-11-01 · Cold pass on the `0a2b7a7` floor re-stamp (`060/100`)](sessions/2026-11-01-1413-floor-restamp-cold-pass.md)

- **2026-11-13** — **Pin bump `0a2b7a7` → `2a6d7a4`; CI green again.** An estate
  health sweep (orchestrator session `e820bff5`) dispatched a headless Opus 5.5
  session. Floor re-stamped word for word (`pins.py`: current, identical); the
  `CI` matrix's 3.8/3.9 Linux entries moved to `ubuntu-22.04` (`070/040` closed);
  FS3 of `060/100` applied. Detail:
  [`docs/sessions/2026-11-13-0608-estate-health-pin-bump.md`](sessions/2026-11-13-0608-estate-health-pin-bump.md).
- [2026-11-13 · 0750 UTC · The session log split into an index and detail files (Opus 5.5, headless, estate health sweep)](sessions/2026-11-13-0750-sessions-log-split.md) — 28 entries moved word for word, proven byte for byte; two relative links rebased.
- [2026-11-14 · 0038 UTC · The commit-message hook added; no record store left to split (Opus 5.5, headless, estate health sweep)](sessions/2026-11-14-0038-commit-msg-hook.md)
- [2026-11-16 · 0602 UTC · Asks de-dupe tidy-ups applied (Opus 5.5, headless, estate health sweep)](sessions/2026-11-16-0602-asks-tidy-applied.md) — C0308 applied (`a77a8f9`); C0311 held, a past session log is not edited.
- [2026-11-16 · 0647 UTC · 🎯 marker removal after the asks tidy-up: nothing to remove (Opus 5.5, headless, estate health sweep)](sessions/2026-11-16-0647-asks-marker-removal.md) — C0308 held: its ask carries ⚠️, not 🎯; no marker commit.
- [2026-11-20 · 1100 UTC · The frozen pre-split archive moved into the board; index rebuilt (Opus 5.5, headless, estate health sweep)](sessions/2026-11-20-1100-board-archive-move.md) — archivecut route (b), verify PASS; index in the new summary form (`df435d5`).
