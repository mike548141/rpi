# 2026-11-20 2222 UTC — The one-file session index retired into the folder

A headless Opus 5.5 session, dispatched by an estate health sweep (orchestrator
session `19378351`), in a detached worktree at `origin/main` (`aa4cfcf`). Its
brief: bring the records to atelier's current form (atelier board `010/220`,
`010/270`). The session log is the `docs/sessions/` folder alone, with no
`docs/SESSIONS.md` index. The frozen board archive had already moved into the
board on 2026-11-20 (`df435d5`), and `docs/SESSIONS-ARCHIVE.md` was never
committed here, so the index was the only thing left to cut.

## What was done

- **Retired `docs/SESSIONS.md`** with atelier's `archivecut.py`. `--plan` and
  `--cut` printed PASS on every proof line. Each of the 34 index lines now sits
  word for word near the top of the session file it linked. The old preamble
  sits fenced in the new `docs/sessions/README.md`. Commit `1be55d8` holds the
  tool's whole change and nothing else. `--verify` printed
  `PASS docs/SESSIONS.md: the README and 34 session files rebuild its last
  committed copy byte for byte`.
- **Updated the text that pointed at the index:** the read order and closing
  rule in `CLAUDE.md` (read the newest few files; write your own
  `YYYY-MM-DD-HHMM-slug.md`), the companion list in `docs/roadmap/README.md`,
  two paragraphs and two hygiene steps in `docs/MODEL-ECONOMICS.md` (the
  touched paragraphs rewrapped at 85), and the stale paths in board items
  `060/010`, `060/030` (a pathscan allow marker on a historical measurement) and
  `060/070` (re-pointed from the folder README to the 2026-08-17 session file
  that holds the entry).
- **`.wrapscanignore`:** dropped the retired file's line and exempted the six
  post-2026-11-01 session files that received a placed line. Those lines must
  stay byte for byte for `--verify`, so they cannot be rewrapped.

## What went wrong first

The first commit attempt chained `git add` with `&&` and the commit with `;`.
The tool had already staged the deletion, so `git add` refused the deleted path
and the commit ran anyway with only that deletion in it. It was caught before
any push. The rest of the tool's change was added to that same unpushed commit
with `--amend`, so the published history holds one complete, verifiable commit.
A rewrap script also computed a slice index before an earlier replacement
shifted the text. The garbled diff was caught on read, and the file was
restored from `HEAD` and redone.

## Left open

- The atelier pin (`2a6d7a4`) is 251 commits behind atelier's `origin/main`,
  and the floor changed in that span. The session-start hook reported it. A
  bump with a verbatim re-stamp is board item `060/010`'s work and was outside
  this brief.
