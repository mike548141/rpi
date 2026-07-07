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
  - **Non-power-of-two wraps** can slip past the corners probes (a fake that wraps at, say, exactly 100 GB with
    no power-of-two structure); the thorough free-space sweep still catches those, so corners is a fast
    first-pass, not a replacement. Could add a few congruence-busting probes for common non-binary sizes.
  - **Wire the corners sweep into `rpi-sdinfo`** (e.g. `--capacity-check --raw --device …`) once it can be tested
    on a real removable card - deliberately not auto-wired yet, since a destructive raw write to the wrong
    device must not ship untested on hardware.
  - Raw-device *full* sweep (not just corners) where we have the device and privileges, so a nearly-full card
    can still be exhaustively tested without needing free space.
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
  - **Still to add — MID that never ships the branded make.** Needs a PNM→brand reverse index over the CID
    database (which is sparse), so it would rarely fire today; deferred until the DB is richer.
- **Decode the CSD register.** ✅ Shipped in 0.7 (`decode_csd()`): structure version → SDSC/SDHC/SDXC/SDUC,
  capacity, TRAN_SPEED bus speed, command classes, read block length - compared against the branding above.

## Data capture & sharing (the "build a public database" idea)

- **Structured output.** ✅ `--format json` ships in 0.5, ✅ local SQLite persistence (`--save-db`) in 0.8.
- **Raw mode.** ✅ Shipped in 0.8 (`--raw`): dumps the full `dumpe2fs` / register / benchmark detail for debugging.
- **Crowd-sourced upload.** Optional POST to an API / S3 bucket so results (CID, CSD, capacity, measured
  performance, pass/fail) build a shared database of card identifiers and real-world failure rates. Needs a
  stronger anonymisation scheme than the current fixed-salt PBKDF2 over the serial (a public salt over a
  low-entropy serial is brute-forceable) — decide what is safe to share before any upload ships.
- **Grow the CID database.** The MID/OID → product table is crowd-sourced and incomplete; every verified
  `CID → real product + measured performance` mapping makes fake-detection stronger.

## Documentation & release polish (post-0.9)

- **Docstrings (documentation-as-code).** The package and `__init__` have docstrings and the code is heavily
  `#`-commented, but the ~116 functions use leading `#` comments rather than `"""docstrings"""`, so `pydoc` /
  `help()` / any API-doc generator shows only signatures. Convert the lead comment of each public function to a
  docstring so the inline documentation is machine-extractable.
- **License.** ✅ Resolved: relicensed to **Apache-2.0** across `LICENSE`, `pyproject.toml` and the per-file
  headers (commit `2e4ed88`), clearing the earlier GPL v2/v3 inconsistency.
- **Tag and publish.** Once the above is settled: tag `v0.9.0`, and decide whether to publish to PyPI (would make
  `pipx install rpi-sdinfo` work without the git URL) — gated on the same "safe to share" review as the upload.
- **Publish an SBOM.** Ship a Software Bill of Materials with each release. The **zero runtime dependencies**
  make this cheap *and* a genuine selling point for a security-adjacent tool: the SBOM is essentially the one
  `rpi-sdinfo` component over the Python stdlib, i.e. a provably tiny supply-chain surface. Decisions to make:
  format (**CycloneDX** vs SPDX — lean CycloneDX JSON, best OWASP/tooling support), generation (a CI job on tag,
  e.g. `cyclonedx-py` for the package or GitHub's dependency-graph export), and delivery (attach to the GitHub
  release, and consider bundling it in the sdist/wheel). Pairs naturally with tag-and-publish and with signing
  the release artifacts. Dev-tooling only — must not add a runtime dependency (ADR 0001).

## Smaller cleanups

- `sdbench`: optional true O_DIRECT path on Linux (aligned buffers) for the most accurate device-level numbers;
  progressively-larger block sizes. ✅ Latency percentiles (not just the mean) shipped in 0.8.
- macOS: ✅ auto-detect a removable card when `--device`/`--dir` is omitted (scans for a removable/external whole
  disk, prefers an SD-bus reader, and points the benchmark at its mount point), and ✅ resolve the card's real
  product/make/serial from a **built-in SD slot** via `system_profiler SPCardReaderDataType`. USB card readers
  still present as generic mass storage, so their card product name remains reader-dependent — no macOS API
  exposes an SD card's CID through a generic USB reader.
- `read_file(return_scope='lines')` only returns a single line; extend it to a range, and test that the `regex`
  scope returns multiple matching lines.
