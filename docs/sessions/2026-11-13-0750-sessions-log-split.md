# 2026-11-13 0750 UTC — the session log split into an index and detail files

A headless Opus 5.5 session, dispatched by an estate health sweep (orchestrator
session `e820bff5`), in a detached worktree at `origin/main`. Its brief: split
the monolithic `docs/SESSIONS.md` into the form atelier's `RECORD.md` describes
(§ *The session log*): a lean index, one line per session, and one detail file
per session under `docs/sessions/`. Mike, 2026-11-13, verbatim, picking the
option "Moves only, nothing deleted": *"Approve all (Recommended)"*.

## What was done

- ✅ **28 entries moved**, one detail file each, word for word. The 2026-11-13
  entry already pointed at its detail file, so it stays in the index as it was.
  The header stays as it was, with one added paragraph saying the file is now
  an index, and an `indexscan` declaration (`dir=sessions match=*.md`).
- ✅ **One file per entry, not per session.** The `(cont.)` entries were each
  appended as their own entry, so each keeps its own file and index line.
- ✅ **Naming, where the entries carry no time.** Every moved entry's heading
  has a date and no time, and its date is the writer's local date: all nine
  2026-07-08 entries landed on 2026-07-07 UTC. So each file is named from the
  UTC time of the commit that first landed the entry (`git log -S` on its first
  line), date and `HHMM` both. That is when the entry was written, not when the
  session started; each file's header says so and names the commit. Each index
  line keeps the entry's own date label, which is never earlier than the file's
  UTC date, so `indexscan`'s date rule holds.
- ✅ **The one byte change: two relative links.** Two entries linked
  `decisions/…` relative to `docs/`; in `docs/sessions/` they would break, so
  both now read `../decisions/…`. The proof below reverses exactly that.
- ✅ **Wrap-width exemption moved with the history.** `.wrapscanignore` already
  exempted `docs/SESSIONS.md` whole as history. The moved files get the same
  exemption by date glob (2026-11-01 and earlier); new detail files are checked.
- ✅ **Read order updated**: `CLAUDE.md` step 2 and `docs/roadmap/README.md`
  now describe the index and where detail goes.

## The proof that it is a move

A script read the original from `git show HEAD:docs/SESSIONS.md`, stripped each
new file's added header, reversed the link rebase, and compared:

| Check | Result |
|---|---|
| Entries in the original | 29 (28 moved, 1 kept as is) |
| Detail files on disk / index links to them | 30 / 30 (with this record) |
| Original moved region | 54,525 bytes, 560 lines |
| Reassembled from the detail files | 54,525 bytes, 560 lines |
| Links rebased, then reversed | 2 |
| Moved region identical, byte for byte | True |
| Kept 2026-11-13 entry identical, only this record's line after it | True |
| Header kept (less the added paragraph) | True |

## Checks

- Floor, whole tree (`floor.py --plane ci`): exit 0. `indexscan` now in scope:
  1 declaration, 29 entries mapped, 28 dated lines compared, clean. `linkscan`,
  `secretscan`, `sizescan`, `spellscan`, `datescan` clean. `wrapscan` (advisory)
  108 → 107. `pathscan` 9 and `pointerscan` 1 are as they were before the split.
- Two false positives on the way, both from this session's own titles, none
  from the moved entries. A title putting the verdict word straight after a
  colon tripped `secretscan`'s assigned-secret rule; a title saying the line
  width was "ruled" tripped `attribscan` (an unquoted attribution). Both were
  reworded and the files regenerated from the original.
- Tests: 182 passed. `CI` and `floor` at the pushed head: see the index line's
  commit and the closing report.

## Identifiers

- **Session**: `da6965c7-befd-4cf9-8d1e-56a366377838`, Opus 5.5, headless;
  window 2026-11-13 from 0750 UTC.
- **Commits**: the split and this record land in one commit.
- **Pull requests**: none.
- **Board**: no item completed, created or claimed.
- **Worktrees and branches**: `~/worktrees/health/rpi-sessions-0750/rpi`,
  detached at `origin/main`, made and removed by the launcher.
- **Agents**: none launched.
- **Other repos**: none written.
