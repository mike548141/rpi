- [ ] **Publish an SBOM.** ◑ Generator shipped: `tools/gen_sbom.py` emits a **CycloneDX 1.5** JSON SBOM, stdlib-only
      (no `cyclonedx-py` — for a zero-dep package the generator itself stays dependency-free), with an empty
      `components` list and a no-dependency root — the "provably tiny supply-chain surface" made machine-readable.
      Format/generation/delivery decisions recorded in [ADR 0005](../../../docs/decisions/0005-sbom-cyclonedx.md); covered by
      `tests/test_sbom.py`. ✅ Now wired into the release workflow (`.github/workflows/release.yml`), which generates
      the SBOM on a `v*` tag and attaches it to the GitHub Release alongside the sdist/wheel. Dev-tooling only — no
      runtime dependency (ADR 0001).
