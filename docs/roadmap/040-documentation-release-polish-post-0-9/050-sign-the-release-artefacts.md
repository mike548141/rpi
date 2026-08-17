- [x] **Sign the release artefacts.** ✅ The release job now keyless-signs the sdist, wheel and SBOM with a
      **GitHub build-provenance attestation** (`actions/attest-build-provenance`): a short-lived Sigstore/Fulcio
      cert minted from the workflow's OIDC identity (no long-lived key), logged to Rekor, emitting a SLSA build
      provenance statement over all three artefacts. The Sigstore bundle is attached to the Release for offline
      checks too. Verify online with `gh attestation verify <file> --repo mike548141/rpi`, or offline with
      `--bundle rpi-sdinfo.sigstore.jsonl`. Chose the GitHub-native action over `sigstore-python`/cosign (no extra
      CI dep, no key to hold, and SLSA provenance for free) — recorded in
      [ADR 0006](../../../docs/decisions/0006-artifact-signing-build-provenance.md). Dev/CI-only — no runtime dependency
      (ADR 0001). Signs only on a real tag push, so the `workflow_dispatch` dry run never mints a cert.
