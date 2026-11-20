# 2026-07-08 (cont. 4) — SBOM generator

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 26+1 -->
- [2026-07-08 (cont. 4) · SBOM generator](2026-07-07-1732-sbom-generator.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `964a1cf`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-08 (cont. 4)**: Shipped the **SBOM generator** — the one release-adjacent item that needs neither
  hardware nor an irreversible decision. `tools/gen_sbom.py` (stdlib-only, dev/release tooling, outside `src/`
  so never in the wheel) emits **CycloneDX 1.5** JSON: single `application` component with `purl`
  `pkg:pypi/rpi-sdinfo@<v>`, SPDX licence `Apache-2.0`, repo as `vcs` ref; **empty `components`** and a root
  that **depends on nothing** — the zero-runtime-dep supply chain made machine-readable (the selling point).
  Version from the package `__version__`; name/licence/repo from `pyproject.toml` via `tomllib` (3.11+) with a
  regex fallback for the 3.6+ floor. `serial_number`/`timestamp` injectable → deterministic under test. Chose a
  stdlib generator over `cyclonedx-py` (overkill to describe nothing) and CycloneDX over SPDX (scanner tooling);
  recorded in **ADR 0005**. Added `tests/test_sbom.py` (7 tests incl. the empty-deps invariant, which also trips
  if a runtime dep ever violates ADR 0001, and the fallback parser). 109 tests green. Docs: ROADMAP item ◑ (gen
  done, on-tag attach remaining), CHANGELOG (Added), CONTRIBUTING (how to generate), `.gitignore` (don't commit
  the artefact). **Next**: the standing v1.0 Pi-hardware blocker; the rest of the release track (tag, PyPI,
  wiring the SBOM into a tag CI job, artifact signing) and the crowd-upload anonymisation scheme all need Mike's
  go-ahead — that's the genuine decision point, not more code.
