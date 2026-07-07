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
  floor) and the ARCHITECTURE-in-shipped-tree/private-doc split (N/A — no secrets). Then (same session) also
  adopted `docs/MODEL-ECONOMICS.md` (Opus builds / Fable reviews, session+token hygiene, measured overhead)
  and added an SBOM-publishing item to the roadmap's release-polish section. Commits: `6306f78` (macOS),
  `9224068` (CSD liar-checks), `599ed57` (bus-ceiling), `1989582` (conventions), + this model-econ/SBOM commit.
  93 tests green; `ruff check .` clean. **Next**: still the standing v1.0 blocker (Pi hardware test); the
  cleanest testable-here item is the congruence-busting non-power-of-two capacity probes in `verify.py`.

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

- **2026-07-08 (cont. 2)**: Did the **docstring conversion** (documentation-as-code). Wrote a one-off
  line-based transform (in scratchpad, not committed) that turns each function's contiguous leading `#` comment
  block into a `"""docstring"""`: tracks multi-line signatures via paren depth, converts only the comment block
  immediately after the `):`, strips one `# ` prefix, and leaves comment-less helpers untouched. Ran it over the
  4 source modules (106 functions documented), reviewed the whole diff by hand — clean, code lines untouched,
  only comment→docstring. Then hand-wrote one-line docstrings for the public entry points that never had a lead
  comment (`main`×3, `parse_args`, `render_report/grade/capacity/db_summary`, `f_num`, `term_width`, `cleanup`).
  Result: **every public function is documented**; a few trivial private helpers (`_pread`, `_open_read`, …) with
  no original lead comment are left bare by design. Verified with an `inspect`-based coverage check (0 public
  undocumented). 96 tests green; `py_compile` clean. `ruff` still not installed locally (CI lints); no D/pydoc
  rules are enabled anyway (`select = E,F,W,C4`) so docstring formatting won't trip it. Docs synced: ROADMAP item
  ✅, CLAUDE.md open-threads (docstrings dropped), CHANGELOG (Changed). Also captured a **product-philosophy**
  note from Mike (see the new memory + below). **Next**: the standing v1.0 Pi-hardware blocker; or
  `read_file(return_scope='lines')` line-range support; or start the v0.9.0 tag / PyPI / SBOM release track.

- **2026-07-08 (cont. 3)**: Also captured the **product-philosophy** point as **ADR 0004** ("honest diagnostic,
  not a pass/fail toy" — the tool diagnoses genuine-but-faulty / worn / honestly-slow / bus-bottlenecked cards,
  not just fakes, for a capable audience; ADR 0003 is its worked example), threaded into the README scope and a
  CLAUDE.md design principle, plus a project memory. Then knocked off the **`read_file` line-range** cleanup:
  the `lines` scope now takes an int (single line), a `(start, stop[, step])` tuple or a `slice` (range, joined),
  or nothing (whole file); an out-of-range int degrades to `''` (a slice just clamps). No caller uses the `lines`
  scope yet, so backward-compat risk is nil. The roadmap's paired ask — that `regex` returns multiple lines — was
  already covered by an existing test; added 6 new `lines` tests. 102 tests green; `py_compile` clean. Docs
  synced (ROADMAP ✅, CHANGELOG). Commits: `d3542ac` (ADR 0004), + this read_file commit. **Next**: the standing
  v1.0 Pi-hardware blocker is the only big rock left that's testable *only* on hardware; the release track
  (v0.9.0 tag / PyPI / SBOM) needs Mike's go-ahead and the anonymisation decision. Bench of small cleanups is
  now essentially drained.

- **2026-07-08 (cont. 4)**: Shipped the **SBOM generator** — the one release-adjacent item that needs neither
  hardware nor an irreversible decision. `tools/gen_sbom.py` (stdlib-only, dev/release tooling, outside `src/`
  so never in the wheel) emits **CycloneDX 1.5** JSON: single `application` component with `purl`
  `pkg:pypi/rpi-sdinfo@<v>`, SPDX licence `Apache-2.0`, repo as `vcs` ref; **empty `components`** and a root
  that **depends on nothing** — the zero-runtime-dep supply chain made machine-readable (the selling point).
  Version from the package `__version__`; name/licence/repo from `pyproject.toml` via `tomllib` (3.11+) with a
  regex fallback for the 3.6+ floor. `serial_number`/`timestamp` injectable → deterministic under test. Chose a
  stdlib generator over `cyclonedx-py` (overkill to describe nothing) and CycloneDX over SPDX (scanner tooling);
  recorded in **ADR 0005**. Added `tests/test_sbom.py` (7 tests incl. the empty-deps invariant, which also trips
  if a runtime dep ever violates ADR 0001, and the fallback parser). 109 tests green. Docs: ROADMAP item ◑ (gen
  done, on-tag attach remaining), CHANGELOG (Added), CONTRIBUTING (how to generate), `.gitignore` (don't commit
  the artifact). **Next**: the standing v1.0 Pi-hardware blocker; the rest of the release track (tag, PyPI,
  wiring the SBOM into a tag CI job, artifact signing) and the crowd-upload anonymisation scheme all need Mike's
  go-ahead — that's the genuine decision point, not more code.

- **2026-07-08 (cont. 5)**: Asked Mike where to go next; he picked **release plumbing for v0.9.0**. Added
  `.github/workflows/release.yml`: triggers on a `v*` tag, **guards that the tag matches `__version__`** (a
  release can't ship a version the code disagrees with), builds sdist + wheel (`python -m build`), generates the
  SBOM (`tools/gen_sbom.py -o dist/rpi-sdinfo.cdx.json`), uploads them as workflow artifacts, and publishes a
  GitHub Release with the tarball/wheel/SBOM attached via `softprops/action-gh-release@v2` +
  `generate_release_notes`. `workflow_dispatch` gives a no-publish dry run. **PyPI push is deliberately NOT
  automated** — left manual pending the safe-to-share review (Mike's call). Validated locally before writing the
  YAML: `python -m build` produces `rpi_sdinfo-0.9.0.{tar.gz,whl}` cleanly, the wheel excludes `tools/`
  (src-layout), the tag-vs-`__version__` one-liner and the YAML both parse. Docs: ROADMAP (tag-and-publish ◑,
  SBOM ✅ wired), CHANGELOG (Added), CONTRIBUTING (a "Cutting a release" section). 109 tests still green (no code
  touched). **To actually release**: bump `__version__` if needed, move CHANGELOG `[Unreleased]` under the
  version, `git tag v0.9.0 && git push origin v0.9.0` — the workflow does the rest. **Next / still open**: the
  Pi-hardware blocker; the PyPI-publish decision; upload anonymisation; artifact signing (sigstore/cosign) could
  bolt onto the release job later.
