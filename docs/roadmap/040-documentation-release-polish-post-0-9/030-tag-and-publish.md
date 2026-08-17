- [ ] 🎯 **Tag and publish.** ◑ Release plumbing shipped: `.github/workflows/release.yml` triggers on a `v*` tag,
      checks the tag matches `__version__`, builds the sdist + wheel, generates the SBOM, and publishes a GitHub
      Release with all three attached (`workflow_dispatch` gives a no-publish dry run). Version is set to **0.9.1**
      and the CHANGELOG `[0.9.1]` section is ready. **Remaining (your call):** actually push the first tag
      (`git tag v0.9.1 && git push origin v0.9.1`), and decide whether to also publish to PyPI (would make
      `pipx install rpi-sdinfo` work without the git URL) — the PyPI push is deliberately *not* automated, gated on
      the "safe to share" review. ✅ **That review is now done and the gate is clear**
      ([ADR 0009](../../../docs/decisions/0009-publish-safety-review.md), 2026-07-29): verdict SAFE TO PUBLISH — leakscan
      11 → 0, secretscan 0 with proven cover, all 63 commits of history scanned clean, licence and attribution
      sound. So PyPI is unblocked on safety grounds; publishing remains your call.
