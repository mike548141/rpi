# 2026-07-08 (cont. 6) — Artefact signing added to the roadmap

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 28+1 -->
- [2026-07-08 (cont. 6) · Artefact signing added to the roadmap](2026-07-07-1742-signing-roadmap-item.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `1640b0b`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-08 (cont. 6)**: Mike okayed **artifact signing** as a future item — added it to the roadmap's
  release-polish section (lean Sigstore/cosign keyless via GitHub OIDC; `sigstore-python` or
  `actions/attest-build-provenance`; emit `.sigstore`/`.sig` bundles onto the same Release; open sub-decisions
  noted; dev/CI-only, no runtime dep per ADR 0001). Docs-only. **End of session.** Session summary — 7 commits:
  `d5c3c83` decimal probes · `1a746cf` docstrings · `d3542ac` ADR 0004 (honest-diagnostic philosophy) · `1b2cbfe`
  read_file range · `964a1cf` SBOM generator (ADR 0005) · `88df93d` release workflow · this docs commit. 109
  tests green throughout. **Nothing pushed** — all local on `main`. **Next session**: the standing v1.0
  Pi-hardware blocker is the only remaining big rock testable *only* on hardware; otherwise everything left is
  Mike-gated (tag `v0.9.0`, PyPI-or-not, upload anonymisation scheme, artifact signing).
