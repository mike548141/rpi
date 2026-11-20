# 2026-07-08 (cont. 8) — Artefact signing shipped

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 30+1 -->
- [2026-07-08 (cont. 8) · Artefact signing shipped](2026-07-07-1825-signing-shipped.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `f32efdc`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-08 (cont. 8)**: Shipped **artifact signing** — the one Mike-okayed release-polish item that needs
  neither hardware nor an irreversible decision. Added keyless build-provenance signing to
  `.github/workflows/release.yml` via `actions/attest-build-provenance@v2`: a short-lived Sigstore/Fulcio cert
  minted from the job's OIDC identity (no long-lived key to hold), logged to Rekor, emitting a SLSA
  build-provenance statement over the sdist, wheel and SBOM. Added `id-token: write` + `attestations: write`
  perms; staged the Sigstore bundle into `dist/` and attached it to the Release so artefacts verify **offline**
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
