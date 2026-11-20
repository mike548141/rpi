# 2026-07-08 (cont. 7) — Release-readiness cleanup

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 29+1 -->
- [2026-07-08 (cont. 7) · Release-readiness cleanup](2026-07-07-1815-release-readiness-cleanup.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `2400ff7`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

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
