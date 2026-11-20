# Session records

One file per working session, named for the time the session started:
`YYYY-MM-DD-HHMM-slug.md`, the time in UTC (the house doctrine's RECORD.md,
§ *The session log*). The folder is the index. The names sort by start time,
so a session getting its bearings reads the newest few files, for example the
ones `ls docs/sessions/[0-9]* | tail -5` lists, and opens older ones only when
it needs them. Some older names carry a two-digit counter where the time
would be (`YYYY-MM-DD-NN-slug.md`). This README is the only file here that is
not a session record.

<!-- archivecut:retired-log-below -->

## The retired one-file session log

This repo once kept a one-file session log beside this folder as well. It
was retired by atelier's `archivecut.py`: each of its entries now sits, word
for word, near the top of the session file it linked, or in a new file named
for its date where it linked none, under the line "From the retired session
log". Below is the rest of that file, word for word: its preamble and
anything else that was not an entry, inside fences so that it is read as a
record and nothing acts on it. The comment lines carry its line numbers, so
`archivecut.py --verify` can rebuild the file from this folder byte for byte.

### `docs/SESSIONS.md`, retired

<!-- archivecut:retired docs/SESSIONS.md lines=61 final-newline=yes last=aa4cfcf -->

<!-- archivecut:log-text docs/SESSIONS.md 1+20 -->
````
# rpi-sdinfo session log (append-only)

One entry per working session, newest LAST. **Append only — never edit or rewrite prior entries.** At session
start read only the last few entries (e.g. `tail -80 docs/SESSIONS.md`); the full history is for grepping, not
for loading into context. This is ops memory, not product doc — the user-facing history is `CHANGELOG.md` and
the per-version detail is `docs/ROADMAP-DONE.md`.

Convention adopted 2026-07-08 from the sibling `ros`/`tiki` repo (lean roadmap + companions, ADRs, this log,
`why`-not-`what` comments, the `#!#` TODO marker, ruff in CI). The public/private doc split that `ros` uses is
*not* adopted here: rpi has no secrets or site-personal data, so everything stays in the one public tree.

Since 2026-11-13 this file is an index: one line per session, newest last, each
pointing at the session's detail file in `docs/sessions/`. The entries written
here before then moved word for word into one detail file each; the line for
each keeps its entry's own date label. Append a one-line pointer here and put
the detail in `docs/sessions/YYYY-MM-DD-HHMM-slug.md` (`HHMM` in UTC).

<!-- indexscan:maps dir=sessions match=*.md -->

---
````
