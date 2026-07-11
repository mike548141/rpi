## Doctrine — inherited from atelier (pinned `atelier@1588fda`)

This repo works by the atelier operating model. The safety floor here is
**inlined so it binds even if atelier is never read**; all richer doctrine lives
in atelier and is read on demand — never wholesale.

- **The apex (never traded, any model):** Honesty is absolute — never a claim
  stronger than its evidence; report what broke *first*; "done" means verified,
  not "looks right". Then the Laws, in order: avoid harm → obey your principal →
  self-preserve. Surface a genuine dilemma; never silently resolve it.
- **Always stop and confirm (the floor):** making a private repo public or
  widening its audience; anything truly destructive or irreversible; secrets;
  spending money; anything touching people's safety; widening your own grant
  (record the principal's decision, never originate it); a lockout-class change
  that could sever your own access; installing an unapproved tool or adding a
  new trust surface (deploy keys, webhooks, OAuth/app grants). Everything
  recoverable — commit/push/PR included — just proceed.
- **Source & drift:** canonical doctrine is `../atelier/docs/method/`. At
  session start run `git -C "../atelier" log --oneline 1588fda..HEAD`; any
  output means the house doctrine moved — read it, then bump the pin above
  deliberately.
- **This repo's visibility:** PRIVATE (a push is not publication; making it public is a floor action). Verify:
  `gh repo view mike548141/rpi --json visibility`.

---

# CLAUDE.md — context for AI sessions on this repo

Orientation for any future session. Canonical detail lives in the docs linked below; this file is the
map, not a copy. Keep it short and current.

## Start-of-session ritual

1. Read [ROADMAP.md](ROADMAP.md) (kept lean — pending work + standing themes).
2. `tail -80 docs/SESSIONS.md` — the append-only session log; the last few entries are where the last session
   left off and what's next. **Append an entry before finishing a session** (newest last, never edit prior ones).
3. Grep the companions on demand, never whole: [docs/ROADMAP-DONE.md](docs/ROADMAP-DONE.md) (per-version
   detail behind roadmap lines), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (the shape), and
   [docs/decisions/](docs/decisions/) (ADRs — read before re-opening a settled call).

## What this repo is

`rpi-sdinfo` — a zero-dependency, cross-platform (Raspberry Pi Linux / macOS / Windows) CLI that identifies,
benchmarks and **fake-checks** SD/MMC cards. Installable `rpi_sdinfo` package (src layout) exposing three
console scripts: `rpi-sdinfo`, `rpi-sdbench`, `rpi-sdverify`. The reason the tool exists is **counterfeit
detection** (capacity fraud + CID/CSD metadata contradictions); everything else supports that.

- **Scope & expectations** (what it is / is not / honest limitations): see the "Scope & expectations" section
  of [README.md](README.md). Short version: a portable *sanity check*, not a certified benchmark or a
  replacement for `f3`/h2testw/`smartctl` — its edge is breadth in one command plus CSD liar-detection.
- **Status, pending work, standing themes:** [ROADMAP.md](ROADMAP.md) (lean); completed-work detail in
  [docs/ROADMAP-DONE.md](docs/ROADMAP-DONE.md).
- **Design shape & decisions:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) + [docs/decisions/](docs/decisions/).
- **Model choice & token/session hygiene:** [docs/MODEL-ECONOMICS.md](docs/MODEL-ECONOMICS.md).
- **History of changes:** [CHANGELOG.md](CHANGELOG.md). **Contributor rules:** [CONTRIBUTING.md](CONTRIBUTING.md).
- **SD card domain knowledge** (CID/CSD, class symbols, fakes): [SD_CARDS.md](SD_CARDS.md).

## Design principles (do not violate without discussing)

- **Honest diagnostic, not a pass/fail toy.** The purpose is broader than fake-catching: also diagnose a
  *genuine* card that is faulty, worn, honestly slow, or bottlenecked by the host/reader/bus. The audience are
  diagnosticians, not luddites — report the real cause at its true severity, don't dumb findings down, and never
  cry "fake" on an inference a genuine card could trip. See [ADR 0004](docs/decisions/0004-honest-diagnostic-not-a-pass-fail-toy.md)
  (and its worked example, [ADR 0003](docs/decisions/0003-tran-speed-is-not-proof-of-fake.md)).
- **Standard library only — zero runtime dependencies.** Must run on stock Pi OS / macOS / Windows Python with
  nothing to `pip install`. Reach for the stdlib before shelling out or adding a dep.
- **Cross-platform, degrade gracefully.** Platform code sits behind `sys.platform`. macOS/Windows can't read the
  SD CID/CSD registers — limited identity there is expected, not a bug.
- **Python 3.6+ floor.** Avoid newer features (e.g. the percentile helper is hand-rolled, not
  `statistics.quantiles`).
- **Keep docs in sync in the same change** — README, ROADMAP, `docs/rpi-sdinfo.1`, CHANGELOG.
- **Comments say _why_, not _what_** — platform quirks, SD-spec reasons, non-obvious constraints earn a comment;
  restating the code does not. `#!#` marks a TODO (more `#` = higher priority).
- **Record real decisions as ADRs.** If you reject a plausible alternative or rest a design on evidence, add a
  short numbered file under [docs/decisions/](docs/decisions/) (Status/Context/Decision/Rejected/Consequences).

## Working conventions in this repo

- **Commit as work completes; don't wait to be asked.** History commits directly to `main`. Only *push* when
  asked. Use the repo's message style + the `Co-Authored-By` trailer.
- **Tests:** `python3 -m unittest discover -s tests` (stdlib `unittest`, no deps, ~3 s). Add/adjust tests with
  behaviour changes and keep the suite green. The package must stay importable via `src/` on the path (tests do
  this through `tests/_loader.py`).
- **Lint:** `ruff check .` (dev-only tool, config in `pyproject.toml`; install via `pip install -e ".[dev]"`).
  Keep it clean — CI runs it. No mypy (the code is un-annotated on a 3.6 floor by choice).
- **CI** (`.github/workflows/ci.yml`) runs ruff + the suite on Linux/macOS/Windows × Py 3.8–3.13. It does **not**
  exercise the Pi sysfs reads — no SD card in CI.
- **Permissions:** keep `.claude/settings.json`'s Bash allow-list broad and prefer the Read/Grep/Edit tools over
  shell text-munging — the user is strongly averse to permission prompts.

## Key constraint & open threads

- **No Pi hardware in the dev environment.** Development is on macOS, so `gather_linux()` and `sdbench`'s
  Linux IO path **cannot be hardware-tested here** — this is the #1 v1.0 blocker. Flag it; don't claim the Linux
  path is verified.
- **Open threads (in ROADMAP):** tagging `v0.9.0` and whether to publish to PyPI; publishing an SBOM on release.
  (Licence is settled — Apache-2.0, ADR 0002. Function docstrings are done.)
