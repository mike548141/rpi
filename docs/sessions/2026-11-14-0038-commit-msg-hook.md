# 2026-11-14 0038 UTC — the commit-message hook, and a records health check

A headless Opus 5.5 session, dispatched by an estate health sweep (orchestrator
session `58027096`, part 2), in a detached worktree at `origin/main`. Its
brief: split any one-file record store that still grows, add the commit-message
hook if missing, and list (outside the repo) the open asks waiting on Mike and
any review owed without a brief.

## What was done

- ✅ **`.githooks/commit-msg` added**, copied from atelier's
  `tools/commit-msg.sample` at the pin. `core.hooksPath` already points at
  `.githooks`, so it runs beside `pre-commit` from this entry's commit on. It
  runs the floor's commit-message plane over each message.
- ✅ **No split needed.** The session log is an index over `docs/sessions/`
  (split 2026-11-13) and the board is one file per item (split 2026-08-17).
  ADRs and reviews are one file each already. `docs/ROADMAP-DONE.md` is frozen
  (155 lines) and stays as it is. `CHANGELOG.md` is the release history, not a
  record store with a split form in the house rules. The 2026-11-13 pin-bump
  index entry carries a four-line summary with its pointer; that is within the
  index form, so it was not moved.
- ✅ **Asks and reviews checked, read-only.** The open asks waiting on Mike are
  the ones already on the board (`030/030`, `040/030`, `050/060`, `060/090`,
  `060/100`, `060/110`). No open item says a cold review is owed without a
  brief.

## Checks

- Floor hook plane on this commit (pre-commit and the new commit-msg hook).
- `CI` and `floor` at the pushed head: see the closing report.

## Identifiers

- **Session**: `85042bf7`, Opus 5.5, headless; window 2026-11-14 from 0038 UTC.
- **Commits**: the hook and this record land in one commit.
- **Pull requests**: none.
- **Board**: no item completed, created or claimed.
- **Worktrees and branches**: `~/worktrees/health/rpi-p2-0038/rpi`, detached
  at `origin/main`, made and removed by the launcher.
- **Agents**: none launched.
- **Other repos**: none written.
