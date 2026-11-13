# 2026-07-29 — Publish-safety review: cleared as the pilot

> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `5b3d753`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Its 1 relative link moved one directory up (`../`); nothing else changed.

- **2026-07-29** — **Publish-safety review — `rpi` cleared as the pilot** (Mike's ask, coordinated from `shed`:
  take the repo to a *verified* safe-to-public state, produce the evidence and the ask, do **not** touch
  visibility). Verdict recorded in [ADR 0009](../decisions/0009-publish-safety-review.md): **SAFE TO PUBLISH** with
  the fixes in this change. Six gates, each with evidence rather than an assurance. **(1) leakscan 11 → 0** —
  every red triaged, all false positives: 8 × the `Mike Clements, Competitive Edge` author byline (deliberate  <!-- leakscan:allow:local-term,nz-address: quotes this review's own triaged findings (author byline / "2 Lane" PCIe comment / "12:00:00" fixture clock) — evidence, not data. See ADR 0009. -->
  attribution; it already ships in the PyPI metadata), 1 × `nz-address` that matched `2 Lane` in a *"PCIe Gen.4  <!-- leakscan:allow: quotes this review's own triaged findings (author byline / "2 Lane" PCIe comment / "12:00:00" fixture clock) — evidence, not data. See ADR 0009. -->
  x 2 Lane"* comment, 2 × `ipv6` that matched `12:00:00` in a `dumpe2fs` fixture. Each got a narrow inline  <!-- leakscan:allow: quotes this review's own triaged findings (author byline / "2 Lane" PCIe comment / "12:00:00" fixture clock) — evidence, not data. See ADR 0009. -->
  `leakscan:allow:` marker with a stated reason — never a blanket ignore; the man page uses a troff `\"` comment
  so the rendered page is unchanged (checked with `mandoc`). The one `.leakscanignore` entry is the
  `src/*.egg-info/` build artefact, already gitignored. **(2) secretscan 0**, re-run from the repo root (the
  positional-path-vs-`--root` footgun avoided) — and 🔎 **cover proved, not assumed**: a planted multi-shape
  canary fired 4 findings and cleared once removed, so the 0 is real rather than a scan that saw nothing.
  **(3) Full history** — all 233 unique blobs across 63 commits extracted and scanned: secretscan **clean**;
  leakscan's 80 hits are the same benign classes plus the FSF's Boston address inside the pre-relicence GPL-2.0
  `LICENSE`. `git log` shows a single human author, so the `2e4ed88` GPL→Apache-2.0 relicence was Mike's to
  make. **No rewrite needed, none done** — and that call was never this session's to take. **(4) Licence** —
  `licenscan` clean, zero third-party imports, `dependencies = []`, nothing vendored, so no copyleft inherited.
  **(5) Reconnaissance** — swept for addressing, hostnames, machine names, estate services, absolute paths:
  nothing. No card serial is ever committed (PSNs are read from sysfs at runtime). **(6) Docs** read as a public
  project. 🎉 **Side effect worth naming: the `floor` workflow is green again** — it had been red on *every* run
  since adoption, `BLOCKED by: leakscan` on those three structural findings, so the scanner backstop was not
  actually gating. 181 tests green; ruff verified clean-of-my-changes in a throwaway venv. **Residual risks Mike
  accepts on a flip** (all in ADR 0009, none blocking): real name + company go public; a personal commit-author
  email sits in all 63 commits' metadata (not reproduced here — `git log --format=%ae`; only a rewrite removes
  it); the repo's honest self-assessment publishes
  too. 🚩 **Pre-existing and NOT fixed here** — CI is red on Windows (`os.geteuid` / `os.pwrite` do not exist
  there) and on two `E402`s a newer `ruff` began enforcing. Unrelated to publish safety, but a public repo wears
  a red badge on its front page; both are Mike's call and a separate track. **Next**: the flip itself (Mike
  alone), then `ros` and `faves` against this now-proven checklist.
