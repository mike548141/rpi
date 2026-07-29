# 0006 — Sign release artefacts with keyless GitHub build-provenance attestations

**Status**: accepted • **Date**: 2026-07-08

## Context

For a security-adjacent tool, a downstream user should be able to prove that the sdist, wheel and SBOM they
downloaded were built by *this* repository's release workflow from *this* tagged commit, and were not tampered
with afterwards. That means signing the artefacts with verifiable provenance.

The release job already builds `dist/*.tar.gz`, `dist/*.whl` and `dist/rpi-sdinfo.cdx.json` (ADR 0005) and
publishes them to a GitHub Release. Signing must bolt onto that job without pulling a long-lived private key
into the repo (a key we would then have to store, rotate and worry about leaking) and — to stay honest to
ADR 0001 — without adding any runtime dependency. It runs only in CI/at release time, so a *build-time* tool is
fine; a *runtime* one is not.

Two decisions to settle: how to sign, and what provenance to emit.

## Decision

- **Sign with `actions/attest-build-provenance`, keyless via the workflow's GitHub OIDC identity.** No
  long-lived key: the action mints a short-lived Sigstore/Fulcio certificate bound to the workflow identity
  (`repo`, ref, commit SHA, runner) and records the signature in the public Rekor transparency log. It needs
  only `id-token: write` (to fetch the OIDC token) and `attestations: write` (to store the attestation) added
  to the job's permissions — nothing to `pip install`.
- **Emit a SLSA build-provenance attestation over all three artefacts.** `subject-path` covers the sdist, wheel
  and SBOM, so each carries a provenance statement (what built it, from which commit/workflow). The action's
  Sigstore bundle is also written into `dist/` and attached to the Release, so the artefacts can be verified
  **offline** from the bundle as well as online.
- **Verification** is `gh attestation verify <file> --repo mike548141/rpi` (online, via the GitHub attestation
  API / Rekor), or `--bundle <the attached .sigstore bundle>` for an air-gapped check. Documented in
  CONTRIBUTING.

## Rejected

- **`sigstore-python` run over the built files.** Also keyless and valid, but it is an extra CI dependency to
  install and pin, and it produces a bare Sigstore signature without the SLSA build-provenance *statement*
  (what/where/how it was built) that `attest-build-provenance` gives for free. The GitHub-native action is less
  to maintain for the same trust guarantee.
- **cosign with a self-managed key pair.** Rejected on the same ground the whole ADR turns on: a long-lived
  private key is a liability (storage, rotation, leak blast-radius) that keyless OIDC signing removes entirely.
  cosign *keyless* would work but is functionally the sigstore-python option with another binary to install.
- **A separate standalone SLSA generator workflow** (`slsa-framework/slsa-github-generator`). Heavier machinery
  than needed; `attest-build-provenance` already produces a SLSA v1 provenance predicate inline in the existing
  release job.

## Consequences

- The release job gains `id-token: write` + `attestations: write` permissions and one signing step; still no
  PyPI push (that stays manual, gated on the "safe to share" review) and still no runtime dependency (ADR 0001).
- Every published sdist/wheel/SBOM is verifiable both online (`gh attestation verify … --repo mike548141/rpi`)
  and offline (against the attached Sigstore bundle).
- Signing runs only on a real tag push (`github.event_name == 'push'`), so the `workflow_dispatch` dry run stays
  side-effect-free — it never mints a certificate or writes to Rekor.
- The signature chain rests on Sigstore/Fulcio/Rekor and the GitHub OIDC identity; if a future release must run
  somewhere without that OIDC trust, the signing step degrades to skipped rather than blocking the build.
