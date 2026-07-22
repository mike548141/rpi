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

- **2026-07-08 (cont. 6)**: Mike okayed **artifact signing** as a future item — added it to the roadmap's
  release-polish section (lean Sigstore/cosign keyless via GitHub OIDC; `sigstore-python` or
  `actions/attest-build-provenance`; emit `.sigstore`/`.sig` bundles onto the same Release; open sub-decisions
  noted; dev/CI-only, no runtime dep per ADR 0001). Docs-only. **End of session.** Session summary — 7 commits:
  `d5c3c83` decimal probes · `1a746cf` docstrings · `d3542ac` ADR 0004 (honest-diagnostic philosophy) · `1b2cbfe`
  read_file range · `964a1cf` SBOM generator (ADR 0005) · `88df93d` release workflow · this docs commit. 109
  tests green throughout. **Nothing pushed** — all local on `main`. **Next session**: the standing v1.0
  Pi-hardware blocker is the only remaining big rock testable *only* on hardware; otherwise everything left is
  Mike-gated (tag `v0.9.0`, PyPI-or-not, upload anonymisation scheme, artifact signing).

- **2026-07-08 (cont. 7)**: Release-readiness cleanup. Found (and fixed) two things blocking a clean tag: (1)
  `src/rpi_sdinfo.egg-info/` was **tracked build output** — untracked it and gitignored `build/`,`dist/`,
  `*.egg-info/` (commit `7a290ca`). (2) **Version story was inconsistent**: `__version__` said 0.9.0, a dated
  `[0.9.0]` changelog section existed, but **no git tag was ever created** and `[Unreleased]` had a whole batch
  of post-0.9.0 work — so tagging `v0.9.0` (which the release workflow guards against `__version__`) would ship
  that work with an out-of-date changelog. Asked Mike; he chose **0.9.1**. Bumped `__version__`→0.9.1,
  consolidated the split `[Unreleased]` Added/Changed blocks into `[0.9.1] - 2026-07-08` (left a fresh empty
  `[Unreleased]`), updated the man-page `.TH` and the ROADMAP tag wording. Verified end-to-end: 109 tests green,
  `python -m build` emits 0.9.1 sdist+wheel, `gen_sbom.py` reports 0.9.1, wheel still excludes `tools/`. Commit
  `c67938f`. **To release now**: `git tag v0.9.1 && git push origin v0.9.1` → the workflow builds, SBOMs and
  publishes the GitHub Release. **Nothing pushed** — 10 local commits on `main` this session
  (`d5c3c83`→`c67938f`). **Next**: the Pi-hardware blocker; PyPI-or-not; upload anonymisation; artifact signing.

- **2026-07-08 (cont. 8)**: Shipped **artifact signing** — the one Mike-okayed release-polish item that needs
  neither hardware nor an irreversible decision. Added keyless build-provenance signing to
  `.github/workflows/release.yml` via `actions/attest-build-provenance@v2`: a short-lived Sigstore/Fulcio cert
  minted from the job's OIDC identity (no long-lived key to hold), logged to Rekor, emitting a SLSA
  build-provenance statement over the sdist, wheel and SBOM. Added `id-token: write` + `attestations: write`
  perms; staged the Sigstore bundle into `dist/` and attached it to the Release so artifacts verify **offline**
  (`gh attestation verify <file> --bundle rpi-sdinfo.sigstore.jsonl`) as well as online (`… --repo
  mike548141/rpi`). Guarded on `github.event_name == 'push'` so the `workflow_dispatch` dry run never mints a
  cert. Chose the GitHub-native action over `sigstore-python`/cosign (no extra CI dep, no key, SLSA provenance
  for free) — recorded as **ADR 0006**. Docs synced: ROADMAP signing item ✅, CHANGELOG `[Unreleased]`/Added
  (post-0.9.1 work, so under Unreleased not 0.9.1), CONTRIBUTING "Cutting a release" (verify commands). No source
  touched; 109 tests green; release.yml parses. Commit `57af8c9`. **Nothing pushed** — now 11 local commits on
  `main` since last sync (`d5c3c83`→`57af8c9`). **Next**: the standing v1.0 Pi-hardware blocker is the only big
  rock left, and it's testable *only* on hardware. Everything else is Mike-gated — tag `v0.9.1` (`git tag v0.9.1
  && git push origin v0.9.1` triggers the now-signing release workflow), the PyPI-publish decision, and the
  crowd-upload anonymisation scheme (needs the "safe to share" call). The testable-here bench is drained.

- **2026-07-09**: Mike asked me to build from the queue until it made sense to stop and save money. The one
  clearly buildable-*and*-testable-here item left was the roadmap's "progressively-larger block sizes" cleanup —
  shipped it as **`--block-sweep`**. `bench.py`: `SWEEP_BLOCKS` (4 KiB→1 MiB), a pure `_sweep_blocks()`
  (clamps each block to the file size and de-dups, so a small file collapses redundant passes), `_fmt_block()`
  (MiB/KiB label), and `block_size_sweep()` reusing `sequential_write()` at each block — one non-destructive
  pass per size over the existing test file. Opt-in flag on **both** entry points: standalone `rpi-sdbench`
  (top-level JSON `block_sweep`) and combined `rpi-sdinfo` (JSON `benchmark.block_sweep`, via `compute_perf`
  stashing on `perf` so it rides `doc['benchmark']` for free), each with a "Block-size sweep" text section. The
  curve is the honest-diagnostic payoff: a genuine card climbs then plateaus past its page/erase granularity, so
  a flat/collapsing/non-scaling curve is a worn-or-fake tell (not a pass/fail). Verified end-to-end on macOS
  (text + JSON, both tools; confirmed absent without the flag) — the measured curve rises 4→64 KiB then plateaus
  as expected. Added 9 tests (2 pure `_sweep_blocks`/`_fmt_block` classes + real-IO sweep + two CLI smoke tests);
  **118 green**, `py_compile` clean; ruff still not installed locally (CI lints). Docs synced: ROADMAP cleanup
  ✅ (O_DIRECT half still needs a Pi), CHANGELOG `[Unreleased]`/Added, man page `--block-sweep`, README example +
  options. Commits `893920d` (bench), `d48ebc3` (cli wiring). **Nothing pushed** — now 13 local commits on `main`
  since last sync (`d5c3c83`→`d48ebc3`). **Next / stopping here to save money**: the testable-here bench is
  genuinely drained again. Everything remaining is hardware-gated (the v1.0 Pi blocker; the non-power-of-two
  arbitrary-wrap raw sweep; the O_DIRECT path) or a Mike decision — tag `v0.9.1`, PyPI-or-not, and the
  crowd-upload **anonymisation scheme** (a real privacy call for a possibly-public tool: what's safe to share,
  and replacing the brute-forceable fixed-salt PBKDF2 over a low-entropy serial). That anonymisation decision is
  the natural next thing to *decide* before more code is worth writing.

- **2026-07-11** — **Adopted into the atelier fleet** (standardise-existing pass,
  pinned `atelier@1588fda`). Prepended the inherited **doctrine block** (apex +
  always-confirm floor + drift check) above the existing onramp; added the
  scanner-floor CI (`.github/workflows/floor.yml`, atelier's public tools run as
  a sibling on every push/PR) and installed the fail-closed pre-commit hook
  (`hooks.atelierTools` → `../atelier/tools`, proven blocking a planted key).
  No other change — rpi was already close to the house standard. Tree scanned
  clean. Next: the crowd-upload anonymisation decision (unchanged).

- **2026-07-12** — **Atelier drift + pin bump, then a CID-database slice.** Start-of-session drift check
  surfaced 5 atelier commits past the pin; the only canonical-method change (`dfd5aec`) adds a RECORD.md rule
  that *public* records keep private siblings generic — it governs atelier's own records, not this private
  repo's, so nothing here needed scrubbing. Read the delta, bumped the pin `1588fda`→`9c63bfc` deliberately
  (`051263c`). Then Mike picked the CID-database thread and I shipped a three-part slice: **(#1)** extracted the
  251-line crowd-sourced `manufacturer` table out of `cli.py` into its own `src/rpi_sdinfo/cid_db.py` verbatim
  (provenance `# CID:` comments intact) so a contribution is a data diff, not code — plus a `validate_cid_db()`
  structural validator and a `leaf_capacity_bytes()` label parser (`8442d3d`; needed a `leakscan:allow` on the
  standard author-header line, which every source file carries). **(#2)** `tests/test_cid_db.py` — asserts the
  shipped table validates clean and proves the validator rejects each fault class (`6fac35d`). **(#3)** the
  **known-good fingerprint capacity cross-check**: when the full CID (MID/OID/PNM/PRV) exactly matches a verified
  product, its label states the capacity, so a card wearing that identity while reporting a grossly different
  size is flagged (`warn` past a 25% band, non-destructive) — `gather` stashes `storage['cid_db_match']`,
  `cross_check` compares (`446691d`). Explicitly **rejected the brand-vs-MID reverse index** as unsound (OEM/ODM
  rebadging → a genuine card legitimately carries another maker's MID; the DB's own Phison→Sony/Lexar/PNY entry
  proves it) — that was the real reason it was "deferred", not DB sparseness. Recorded as **ADR 0007** with docs
  synced (ROADMAP both CID items, CHANGELOG, README CONSISTENCY, CONTRIBUTING how-to) (`a2a9231`). 138 tests
  green throughout; all pre-commit floor scanners clean. **Nothing pushed** — 6 local commits on `main` since
  last sync (`051263c`→`a2a9231`). **Next**: unchanged big rocks — the v1.0 Pi-hardware blocker (only testable
  on hardware) and the Mike-gated decisions (crowd-upload anonymisation scheme, tag `v0.9.1`, PyPI-or-not). The
  CID DB is now structured to *grow* — but growing it needs real observed cards, never invented mappings.

- **2026-07-22** — **First orchestrated queue run** (Fable orchestrating, three Opus agents in parallel
  worktrees; Mike's ask: maximise plan use, take the small/unblocking/nearly-done work first). Doctrine drift
  read (targeted: CONCURRENCY + AUTONOMY deltas; floor unmoved), pin bumped `2b8da3b`→`9e7e031`; the new
  claim-on-main mechanism was used for real — three items claimed `[~]` on `main` before work, each built on
  its own branch/worktree, merged, claim resolved, branch put away. Landed: **(1) brand-set signal, first
  slice** (`brand_sets()`/`brands_observed()`/`validate_brand_sets()` derived live from the CID table; neutral
  `info` context in `cross_check()`; product *labels* deliberately not mined — prose boundaries would fabricate
  brands; +35 tests). **(2) ADR 0008 crowd-upload anonymisation** (Proposed — Mike's ruling owed on five
  questions). 🔎 Its grounding pass corrected a real misconception: the local PBKDF2 hashes the **Pi host**
  serial, not the card's — the card PSN sits in the local DB in the clear, so an upload payload must be
  purpose-built, never a subset of the local row. **(3) raw-device full sweep** (`rpi-sdverify --device --full`,
  write-all-then-verify-all so wraps corrupt before read-back; O(one block) memory; proof-test where a 33-block
  arbitrary-wrap fake passes corners but is caught by full; +8 tests). File-tested only — hardware validation
  joins the Pi blocker. Known nuance (recorded, not fixed): on a pure-modulo wrap the first mismatch lands at
  offset 0, so `usable_estimate_bytes` reads 0 — honest (the head really is clobbered) but differs from a
  truncating fake, which pins the mismatch at the real boundary. 138→**181 tests green** on `main`; ruff not
  installed locally (CI lints); everything pushed as it landed (per the 2026-07-10 standing grant + concurrency
  doctrine — the old "Mike syncs himself" habit is retired). **Next**: all remaining work is gated — Pi
  hardware (v1.0 blocker; corners/full/O_DIRECT validation), Mike's rulings (ADR 0008's five questions; tag
  `v0.9.1`; PyPI-or-not), or real cards (CID DB growth). The suspicion score stays deliberately deferred until
  the brand table is richer (own ADR when it comes).
