# rpi-sdinfo roadmap

What's left before a v1.0, and the standing themes. Kept **lean** — it is read at every session start. Companion
docs (grep on demand, never load whole):

- [`docs/ROADMAP-DONE.md`](docs/ROADMAP-DONE.md) — the per-version completed-work detail (0.3 → post-0.9).
- [`docs/SESSIONS.md`](docs/SESSIONS.md) — append-only session log; read the tail at session start, append an
  entry before finishing.
- [`docs/decisions/`](docs/decisions/) — ADRs: decisions where a plausible alternative was rejected or a design
  rests on evidence (e.g. why a fake is *not* inferred from TRAN_SPEED).
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — the gather→compute→render shape and the two fake-detection
  strategies.
- [`docs/MODEL-ECONOMICS.md`](docs/MODEL-ECONOMICS.md) — which model does what, and session/token hygiene.
- [`CHANGELOG.md`](CHANGELOG.md) — user-facing change history.

Done through 0.9 (packaging, native benchmark, capacity sweep, CSD decode + cross-checks, SQLite history, latency
percentiles, the test suite) plus the post-0.9 macOS/CSD work lives in `docs/ROADMAP-DONE.md`. The bash original
(`archive/rpi-sdinfo.sh`) is reference only, not developed further.

## Next up (v1.0 blockers)

- **Not yet hardware-tested on a Pi.** The macOS path is exercised end-to-end (and now unit-tested); the Linux
  `gather_linux()` path is preserved from the working 0.3 logic and compiles, but the sysfs-dependent parts still
  need a run on a real Pi 3B and Pi Zero W. Watch:
  - `sdbench` write/read units and whether the F_NOCACHE/O_DSYNC path reports realistic SD numbers on a Pi
    (validate against the old fio results and a known card).
  - `dumpe2fs` / `meminfo` label spellings across Raspberry Pi OS versions.
  - `/proc/diskstats` column count/order for the read/write counters.
  - The new `erase_size == 0` branch: confirm a real not-block-addressed card actually reports 0 and that the
    assumed-512 capacity + `info` flag read sensibly (only the pure logic is unit-tested; the sysfs read is not).

## Fake / counterfeit card detection (the reason the tool exists)

- **Capacity fraud test.** ✅ Shipped in 0.6 (`sdverify.py`, `--capacity-check`) and since extended with a
  raw-device **corners sweep** (`sdverify.py --device`): probes block 0, every power-of-two offset, and the last
  block of the reported capacity. Because a fake truncates the block address at a power-of-two boundary R, block
  0 and block R alias onto one physical cell, so the (0, R) pair is always probed — a guaranteed catch for any
  power-of-two address-truncation fake (the standard kind) in ~log₂(N) probes rather than a full-card write.
  Destructive, so gated behind `--yes` and a mounted-device refusal. Still to refine:
  - **Non-power-of-two wraps.** ✅ The corners sweep now also probes each common decimal capacity boundary below
    the reported size (`COMMON_FAKE_CAPACITIES_BYTES`), so a fake that wraps at a round decimal size (e.g. a real
    8 GB chip reporting 512 GB) aliases that boundary onto block 0 and is caught. A *truly arbitrary* wrap (no
    round boundary) can still slip past both the power-of-two and decimal probes; the thorough free-space sweep
    remains the exhaustive backstop, so corners stays a fast first-pass, not a replacement.
  - **Wire the corners sweep into `rpi-sdinfo`** (e.g. `--capacity-check --raw --device …`) once it can be tested
    on a real removable card - deliberately not auto-wired yet, since a destructive raw write to the wrong
    device must not ship untested on hardware.
  - Raw-device *full* sweep (not just corners) where we have the device and privileges, so a nearly-full card
    can still be exhaustively tested without needing free space. `[~ claimed 2026-07-22-1035 UTC, wt:
    rpi-full-sweep]`
- **CID/CSD cross-checks.** ✅ Shipped in 0.7 (`cross_check()`): flags a Standard-Capacity CSD claiming a
  high/extended capacity (impossible), a CSD-vs-reported capacity mismatch, and a future manufacturing date.
  ✅ Extended (post-0.9): **structural-validity liar-checks** on the register itself — reserved CSD structure
  version (3), a zero/undefined TRAN_SPEED, empty or missing-mandatory command classes (basic/read/write), and
  an illegal READ_BL_LEN. A genuine controller emits a spec-valid register, so garbage here is a counterfeit
  tell (all `warn` severity — strong hints, not exit-code fails).
  - **Rated class vs TRAN_SPEED — surfaced as `info`, never as a fail.** Inferring "this card can't be A2/U3"
    from a low TRAN_SPEED is *unsound*: UHS bus speed is negotiated out-of-band (CMD6/CMD11), so a genuine UHS
    card legitimately still reports 25/50 Mbit/s in the legacy field. Failing on it would poison credibility.
    Instead, when the rated class exceeds what the advertised bus can carry (e.g. a U3/V30 card on a high-speed
    ~25 MB/s bus), the tool emits an **info** note explaining the ceiling — so a genuine card measuring below
    its label is understood (bus-limited on a non-UHS host), not silently believed fast or assumed broken.
  - **Known-good fingerprint capacity cross-check.** ✅ Shipped (post-0.9.1): when the full CID
    (MID/OID/PNM/PRV) exactly matches a *verified* product in the database, that product's label states its
    capacity, so a card wearing that exact identity while reporting a grossly different size is flagged (`warn`
    past a 25% band; a clone flashed to lie about capacity, caught with no destructive write). Fires rarely today
    but is sound every time it does, and strengthens as the DB grows.
  - **Brand↔MID as a learned, *scored* signal (not a binary tell).** `[~ claimed 2026-07-22-1021 UTC, wt:
    rpi-brand-set — first slice only: structured brand-set data model + neutral info finding]` The naive "brand≠MID ⇒ fake" trigger is
    unsound (OEM/ODM rebadging — the DB's own Phison→Sony/Lexar/PNY entry proves a genuine card carries another
    maker's MID). But the brand↔MID *relationship* is real, learnable data: structure the free-text OEM string
    into a countable **set of brands observed shipping under each MID/OID**, growing with every real card, and let
    a well-populated pairing nudge toward genuine / a never-seen pairing nudge toward suspect. Feeds a **heuristic
    suspicion score**, never a verdict. Design constraints (from [ADR 0007 addendum](docs/decisions/0007-fingerprint-capacity-not-brand-reverse-index.md)):
    - **Hybrid, so [ADR 0004](docs/decisions/0004-honest-diagnostic-not-a-pass-fail-toy.md) holds** — spec-impossible facts stay hard `fail`s that drive the
      exit code; soft signals (brand-set, capacity-vs-fingerprint, register oddities, date, TRAN_speed context)
      aggregate into a *separate, explained* score, always shown with its contributing reasons, never a bare light.
    - **Suspicion index, not P(fake)** — no labelled ground truth to calibrate a probability, so never print a
      percentage; a heuristic score with named signals is the honest artefact.
    - **Unknown ≠ suspicious early** — an unseen pairing pulls near-neutral until the maker is well-observed, so a
      genuine oddball isn't punished for a thin table.
    - Build incrementally: first the structured brand-set data model + a neutral "consistent with known brands for
      this maker" **info** finding (zero risk, starts accumulating value); the aggregate score comes later, once
      the table is rich enough for weights to mean anything, and earns its own ADR then.
- **Decode the CSD register.** ✅ Shipped in 0.7 (`decode_csd()`): structure version → SDSC/SDHC/SDXC/SDUC,
  capacity, TRAN_SPEED bus speed, command classes, read block length - compared against the branding above.

## Data capture & sharing (the "build a public database" idea)

- **Structured output.** ✅ `--format json` ships in 0.5, ✅ local SQLite persistence (`--save-db`) in 0.8.
- **Raw mode.** ✅ Shipped in 0.8 (`--raw`): dumps the full `dumpe2fs` / register / benchmark detail for debugging.
- **Crowd-sourced upload.** `[~ claimed 2026-07-22-1021 UTC, wt: rpi-anon-scheme — anonymisation-scheme
  design + draft ADR for Mike's ruling; no upload code]` Optional POST to an API / S3 bucket so results (CID, CSD, capacity, measured
  performance, pass/fail) build a shared database of card identifiers and real-world failure rates. Needs a
  purpose-built anonymisation scheme, not a subset of the local row: the card serial (PSN) is only 32 bits, so
  any public-salt hash over it is brute-forceable, and shipping the full CID uploads a unique per-card
  fingerprint outright (the local fixed-salt PBKDF2 hashes the *Pi host* serial, not the card, and does no
  upload-anonymisation work). Draft design + threat model + recommendation:
  [docs/decisions/0008-crowd-upload-anonymisation.md](docs/decisions/0008-crowd-upload-anonymisation.md)
  (Proposed — awaiting Mike's ruling on what is safe to share; no upload ships before it).
- **Grow the CID database.** The MID/OID → product table is crowd-sourced and incomplete; every verified
  `CID → real product + measured performance` mapping makes fake-detection stronger. ✅ The table now lives in
  its own file (`src/rpi_sdinfo/cid_db.py`) so a contribution is a data diff, not a code change, gated by a
  structural validator (`validate_cid_db`) the suite runs on every change. Still just needs *more real cards* —
  each verified fingerprint also arms the capacity cross-check above.

## Documentation & release polish (post-0.9)

- **Docstrings (documentation-as-code).** ✅ Done: every function with a leading `#` comment now carries a
  `"""docstring"""` (converted by a one-off transform, reviewed by hand), and the public entry points that had
  no lead comment (`main`, `parse_args`, the `render_*` family, `f_num`, `term_width`, `cleanup`) got a
  hand-written one-liner. `pydoc` / `help()` / any API-doc generator now shows the intent, not just signatures.
  Every *public* function is documented; a handful of trivial private helpers (`_pread`, `_open_read`, …) that
  never had a lead comment are left bare by design.
- **License.** ✅ Resolved: relicensed to **Apache-2.0** across `LICENSE`, `pyproject.toml` and the per-file
  headers (commit `2e4ed88`), clearing the earlier GPL v2/v3 inconsistency.
- **Tag and publish.** ◑ Release plumbing shipped: `.github/workflows/release.yml` triggers on a `v*` tag,
  checks the tag matches `__version__`, builds the sdist + wheel, generates the SBOM, and publishes a GitHub
  Release with all three attached (`workflow_dispatch` gives a no-publish dry run). Version is set to **0.9.1**
  and the CHANGELOG `[0.9.1]` section is ready. **Remaining (your call):** actually push the first tag
  (`git tag v0.9.1 && git push origin v0.9.1`), and decide whether to also publish to PyPI (would make
  `pipx install rpi-sdinfo` work without the git URL) — the PyPI push is deliberately *not* automated, gated on
  the "safe to share" review.
- **Publish an SBOM.** ◑ Generator shipped: `tools/gen_sbom.py` emits a **CycloneDX 1.5** JSON SBOM, stdlib-only
  (no `cyclonedx-py` — for a zero-dep package the generator itself stays dependency-free), with an empty
  `components` list and a no-dependency root — the "provably tiny supply-chain surface" made machine-readable.
  Format/generation/delivery decisions recorded in [ADR 0005](docs/decisions/0005-sbom-cyclonedx.md); covered by
  `tests/test_sbom.py`. ✅ Now wired into the release workflow (`.github/workflows/release.yml`), which generates
  the SBOM on a `v*` tag and attaches it to the GitHub Release alongside the sdist/wheel. Dev-tooling only — no
  runtime dependency (ADR 0001).
- **Sign the release artifacts.** ✅ The release job now keyless-signs the sdist, wheel and SBOM with a
  **GitHub build-provenance attestation** (`actions/attest-build-provenance`): a short-lived Sigstore/Fulcio
  cert minted from the workflow's OIDC identity (no long-lived key), logged to Rekor, emitting a SLSA build
  provenance statement over all three artifacts. The Sigstore bundle is attached to the Release for offline
  checks too. Verify online with `gh attestation verify <file> --repo mike548141/rpi`, or offline with
  `--bundle rpi-sdinfo.sigstore.jsonl`. Chose the GitHub-native action over `sigstore-python`/cosign (no extra
  CI dep, no key to hold, and SLSA provenance for free) — recorded in
  [ADR 0006](docs/decisions/0006-artifact-signing-build-provenance.md). Dev/CI-only — no runtime dependency
  (ADR 0001). Signs only on a real tag push, so the `workflow_dispatch` dry run never mints a cert.

## Smaller cleanups

- `sdbench`: optional true O_DIRECT path on Linux (aligned buffers) for the most accurate device-level numbers.
  ✅ Latency percentiles (not just the mean) shipped in 0.8. ✅ **Progressively-larger block sizes** shipped as
  `rpi-sdbench --block-sweep` (post-0.9.1): an opt-in sequential-write throughput-vs-block-size curve (4 KiB →
  1 MiB), diagnostic of a controller whose small-block writes collapse or never scale. The O_DIRECT path still
  needs a real Pi to validate.
- macOS: ✅ auto-detect a removable card when `--device`/`--dir` is omitted (scans for a removable/external whole
  disk, prefers an SD-bus reader, and points the benchmark at its mount point), and ✅ resolve the card's real
  product/make/serial from a **built-in SD slot** via `system_profiler SPCardReaderDataType`. USB card readers
  still present as generic mass storage, so their card product name remains reader-dependent — no macOS API
  exposes an SD card's CID through a generic USB reader.
- ✅ `read_file(return_scope='lines')` now takes a range as well as a single index: an int returns one line, a
  `(start, stop[, step])` tuple or a `slice` returns that range joined, and an out-of-range int degrades to `''`
  per the no-traceback contract. The `regex` scope's multi-line return is covered by a test.
