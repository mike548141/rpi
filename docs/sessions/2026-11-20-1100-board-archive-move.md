# 2026-11-20 1100 UTC — The frozen pre-split archive moved into the board; index rebuilt

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 61+1 -->
- [2026-11-20 · 1100 UTC · The frozen pre-split archive moved into the board; index rebuilt (Opus 5.5, headless, estate health sweep)](2026-11-20-1100-board-archive-move.md) — archivecut route (b), verify PASS; index in the new summary form (`df435d5`).


A headless Opus 5.5 session, dispatched by an estate health sweep (orchestrator
session `19378351`), in a detached worktree at `origin/main` (`d8c8ed4`). Its
brief had two parts: cut the frozen pre-split archives into their stores with
atelier's `archivecut.py`, then rebuild the board index in `board.py`'s new
form (a summary table plus unfinished items only).

💬 Mike's answer, 2026-11-20, to a structured question from the sweep (a pick
from its options, not a ruling), verbatim: "Split, fall back to move
(Recommended)". It followed his words the same day, verbatim: "I think we
should find a way that the old ROADMAP-DONE.md is either split back out into
files to match the current design for board work management. Or worst case if
that is not going to work or ruin the historical record held in
ROADMAP-DONE.md then we create a theme folder to store ROADMAP-DONE.md in so
its not in the docs/ folder anymore".

## What ran

| Step | Result |
|---|---|
| `archivecut.py --plan` | Route (b), moved whole: `FAIL 0 [x] entries found`, so a cut into item files could not prove itself. Every other proof line PASS, including "route (b): 2 link paths re-pointed in the moved file, each maps back to its original". |
| `archivecut.py --cut` | `docs/ROADMAP-DONE.md` (last changed in `4bd429c`) moved to `docs/roadmap/990-done-before-the-split/frozen/`, with a section README. Links to it from `CLAUDE.md`, the board README and item 060/070 were re-pointed. |
| Fixes the move caused | The `.wrapscanignore` history glob now names the new folder. Two plain-text mentions (`docs/MODEL-ECONOMICS.md`, `docs/roadmap/README.md`) now point at the new place. |
| `board.py --rebuild` | `docs/ROADMAP.md` is in the new form, 80 lines. `--check`: current. |
| `archivecut.py --verify` | `PASS  docs/ROADMAP-DONE.md: route (b), the moved file maps back to its last committed copy`. `docs/SESSIONS-ARCHIVE.md` was never committed here, so there was nothing to do. |

The move and the rebuilt index are one commit, `df435d5`. The new 990 section
leaves an old-form index stale, so the pre-commit `board` check would have
refused the move on its own.

## Checks

- Floor, ci plane, whole tree: every enforced check passes, `board` included.
  `wrapscan` stays advisory under its declared backlog (060/110).
- CI at `df435d5`: `CI` success
  (<https://github.com/mike548141/rpi/actions/runs/44723939678>), `floor`
  success (<https://github.com/mike548141/rpi/actions/runs/44723940101>).
- The first wording of the `MODEL-ECONOMICS.md` line kept the old path as
  history, and warn-only `pathscan` flagged it as missing. This commit rewords
  it.

## Seen, not acted on

- `.atelier-floor.json` does not declare `"visibility": "public"`, though the
  repo is public, so `namescan` and `pdlistscan` report "not in scope" here.
  Declaring it is outside this run's brief, and it turns on checks that have
  not run over this tree. It is reported to the sweep.
- The atelier pin (`2a6d7a4`) is behind atelier's mainline and the floor has
  changed since. That is board item 060/010's work, not this run's.
