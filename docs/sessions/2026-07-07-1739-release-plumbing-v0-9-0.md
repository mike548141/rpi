# 2026-07-08 (cont. 5) — Release plumbing for v0.9.0

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 27+1 -->
- [2026-07-08 (cont. 5) · Release plumbing for v0.9.0](2026-07-07-1739-release-plumbing-v0-9-0.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `88df93d`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-08 (cont. 5)**: Asked Mike where to go next; he picked **release plumbing for v0.9.0**. Added
  `.github/workflows/release.yml`: triggers on a `v*` tag, **guards that the tag matches `__version__`** (a
  release can't ship a version the code disagrees with), builds sdist + wheel (`python -m build`), generates the
  SBOM (`tools/gen_sbom.py -o dist/rpi-sdinfo.cdx.json`), uploads them as workflow artefacts, and publishes a
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
