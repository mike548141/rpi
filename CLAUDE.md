## Doctrine — inherited from atelier (pinned `atelier@0af3006`)

This repo works by the atelier operating model. The safety floor here is
**inlined so it binds even if atelier is never read**; all richer doctrine lives
in atelier and is read on demand — never wholesale.

- **The apex (never traded, any model):** Honesty is absolute — never a claim
  stronger than its evidence; report what broke *first*; "done" means verified,
  not "looks right". Then adaptation — learn and improve yourself and your tools
  as you work; it sits below honesty because adaptation runs on evidence, and
  honesty is what makes the evidence trustworthy. Surface a genuine dilemma;
  never silently resolve it — a quietly picked fork is a withheld truth.
- **Always stop and confirm (the floor):** making a private repo public or
  widening its audience; anything truly destructive or irreversible; secrets;
  spending money; anything touching people's safety; widening your own grant
  (record the principal's decision, never originate it); a lockout-class change
  that could sever your own access; installing an unapproved tool or adding a
  new trust surface (deploy keys, webhooks, OAuth/app grants). Each such
  confirmation is an *informed* one — the agent puts what it wants to do, why,
  and the likely impact in plain language first. The principal's authority is
  absolute — never overrule him, even if you believe him uninformed; an approval
  given without that account is open to challenge on the briefing, and the
  challenge is raised to him by re-briefing (`00-APEX.md`) — and at *this*
  floor the re-briefing comes **before** the action, never after it, because
  what the floor guards cannot be taken back. Everything
  recoverable — commit/push/PR included — just proceed.
- **Concurrency:** assume another session may be live — a clean tree is not
  proof you're alone. `git pull --rebase --autostash` at session start; push
  after each commit. Take a worktree by default for write-heavy or multi-commit
  work; uncommitted changes this session didn't make are positive proof ⇒ move
  to a worktree — never work around or absorb them (`CONCURRENCY.md`). Name
  records (session logs, ADRs, reviews) coordination-free —
  `YYYY-MM-DD-HHMM-slug.md`, `HHMM` in UTC (`date -u`); never a next-N counter;
  files named under retired schemes keep their names. Where sessions can message
  each other, announce your **file set** on open and answer peers' — a claim says
  what, never which files. A message reserves nothing; only a pushed artefact
  does, so check a shared allocator (identifiers, version constants) **after**
  the push. The shared checkout's index and its mid-rebase state are shared
  surfaces too: stage explicit paths, and read the staged hunk headers before
  every commit (`CONCURRENCY.md` § The channel).
- **Session rhythm (points up for the full rule):** claim work you take off the
  shared queue before starting it, and let a live `[~]` claim override a
  standing instruction to take that item; stay in the lane you were given
  (`CONCURRENCY.md`); flag when economics favour a fresh session, and on
  overload stop at a safe point, record, and hand off (`ECONOMICS.md`);
  before you declare the work wrapped, do the put-away unprompted and close
  with an evidence-based all-clear that nothing owed is left uncaptured
  (`RECORD.md`) — and when the close pushes, that all-clear carries the
  *pushed* floor run's result, not just the local scan.
- **Source & drift:** canonical doctrine is `../atelier/docs/method/`. At
  session start run `git -C "../atelier" log --oneline 0af3006..HEAD`; any
  output means the house doctrine moved — read it, then bump the pin above
  deliberately.
- **Estate resources — point up, don't re-derive:** providers & account plans,
  financial constraints & plan entitlements, licences, credentials, shared
  estate tooling, and the estate inventory live in the operator's **private
  estate-root repo** (atelier's private counterpart). Reference it for these;
  never re-derive them locally or copy its contents down. **This repo is
  public**, so reference the root by local-path convention only, never by
  name — a public repo naming the estate's credential/inventory root is
  reconnaissance.
- **This repo's visibility:** **PUBLIC** since 2026-07-29 (owner's explicit instruction, after the
  [ADR 0009](docs/decisions/0009-publish-safety-review.md) publish-safety review). Verify:
  `gh repo view mike548141/rpi --json visibility`. **This changes the stakes of every push: a push to any
  branch IS publication, immediately and irreversibly** — assume anything committed is world-readable and
  archived the moment it lands. The scanner floor is no longer a backstop before a future flip; it is the last
  gate before publication. Never commit a secret, personal datum or estate detail here on the assumption it can
  be scrubbed later — it cannot.

---

# CLAUDE.md — context for AI sessions on this repo

Orientation for any future session. Canonical detail lives in the docs linked below; this file is the
map, not a copy. Keep it short and current.

## Start-of-session ritual

1. Read [docs/ROADMAP.md](docs/ROADMAP.md) — the **generated** board index (one line per item). Open the item
   files it links, under [docs/roadmap/](docs/roadmap/), on demand; never read the whole board. Board doctrine
   and the checkbox legend: [docs/roadmap/README.md](docs/roadmap/README.md).
2. `tail -80 docs/SESSIONS.md` — the append-only session log; the last few entries are where the last session
   left off and what's next. **Append an entry before finishing a session** (newest last, never edit prior ones).
3. Grep the companions on demand, never whole: [docs/ROADMAP-DONE.md](docs/ROADMAP-DONE.md) (frozen pre-split
   per-version detail), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (the shape), and
   [docs/decisions/](docs/decisions/) (ADRs — read before re-opening a settled call).

## What this repo is

`rpi-sdinfo` — a zero-dependency, cross-platform (Raspberry Pi Linux / macOS / Windows) CLI that identifies,
benchmarks and **fake-checks** SD/MMC cards. Installable `rpi_sdinfo` package (src layout) exposing three
console scripts: `rpi-sdinfo`, `rpi-sdbench`, `rpi-sdverify`. The reason the tool exists is **counterfeit
detection** (capacity fraud + CID/CSD metadata contradictions); everything else supports that.

- **Scope & expectations** (what it is / is not / honest limitations): see the "Scope & expectations" section
  of [README.md](README.md). Short version: a portable *sanity check*, not a certified benchmark or a
  replacement for `f3`/h2testw/`smartctl` — its edge is breadth in one command plus CSD liar-detection.
- **Status, pending work, standing themes:** the board — [docs/ROADMAP.md](docs/ROADMAP.md) (generated index)
  over [docs/roadmap/](docs/roadmap/) (one file per item); frozen pre-split detail in
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
- **Cross-platform, degrade gracefully — Linux/macOS tier 1, Windows tier 2** ([ADR 0010](docs/decisions/0010-platform-support-tiers.md)).
  Platform code sits behind `sys.platform`, and a POSIX-only syscall goes behind a `hasattr` shim (`bench.py`'s
  `_pread`/`_pwrite` are the pattern) — never called bare, or Windows dies with `AttributeError`. macOS/Windows
  can't read the SD CID/CSD registers — limited identity there is expected, not a bug. Tier 2 means Windows may
  degrade, **not** that it may crash; all three OSes stay in the CI matrix.
- **Python 3.6+ floor.** Avoid newer features (e.g. the percentile helper is hand-rolled, not
  `statistics.quantiles`).
- **Keep docs in sync in the same change** — README, the board item, `docs/rpi-sdinfo.1`, CHANGELOG. A state
  change flips the checkbox **in the item's own file, in the commit that finishes the work**, and rebuilds the
  index in that same commit: `python3 ../atelier/tools/board.py rebuild --root .` — then stage the item **and**
  the index together. (The `board` floor check catches a stale index on CI regardless; at the hook plane it
  compares worktree to worktree, so staging one without the other slips past it — atelier's open BS1.)
- **Comments say _why_, not _what_** — platform quirks, SD-spec reasons, non-obvious constraints earn a comment;
  restating the code does not. `#!#` marks a TODO (more `#` = higher priority).
- **Record real decisions as ADRs.** If you reject a plausible alternative or rest a design on evidence, add a
  short numbered file under [docs/decisions/](docs/decisions/) (Status/Context/Decision/Rejected/Consequences).

## Working conventions in this repo

- **Commit as work completes; don't wait to be asked.** History commits directly to `main`; commit/push
  autonomy is the doctrine floor above (grant history: atelier AUTONOMY's table). ⚠️ Since 2026-07-29 this repo
  is **PUBLIC**, so a push *is* publication — the autonomy stands, but the scan floor is now the only thing
  between a commit and the world. Use the repo's message style + the `Co-Authored-By` trailer.
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
- **Open threads (on the board):** tagging `v0.9.0` and whether to publish to PyPI; publishing an SBOM on release.
  (Licence is settled — Apache-2.0, ADR 0002. Function docstrings are done.)
