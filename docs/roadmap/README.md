# rpi-sdinfo ROADMAP — the board

What's left before a v1.0, and the standing themes. **One file per item**
(atelier's board-store ADR, Mike ruled 2026-08-15; adopted here 2026-08-17).
Each item lives in `<NNN>-<section>/<NNN>-<slug>.md`: its checkbox line first,
detail beneath, its own `git log` as provenance — which commit flipped its
state, and what work that commit carried. Each section's narrative is that
section's `README.md`. [`../ROADMAP.md`](../ROADMAP.md) is the **generated
index** (atelier's `../atelier/tools/board.py`, a path relative to this repo's root; the `board` floor check blocks a commit
whose index is stale — after a merge conflict on the index, rebuilding *is* the
resolution). The session-start read is the index; open item files on demand.

Checkbox states — a **work-owed tri-state**, never a disposition:
`[ ]` work still owed · `[x]` **no more work owed** — delivered, superseded or
declined, with the disposition said in the item's own text · `[~]` **claimed**
by a live parallel session (`(claimed <date>-<HHMM>, wt: <branch>)`) — don't
start a `[~]` item, take the next open one · `⏳` **review queued** for a
non-author to take. A state change **rebuilds the index in the same commit**;
the `board` check makes that mechanical rather than remembered.

Continuation lines are indented **≥4 columns**. That is grammar, not style: the
house item parser treats a line indented less than 4 as the *end* of the item,
so a 2-column body is invisible to `harvestscan`'s survivor search — the net
that catches an item deleted without its work being done.

Companion docs (grep on demand, never load whole):

- [`docs/ROADMAP-DONE.md`](../ROADMAP-DONE.md) — **frozen** pre-split per-version completed detail (0.3 → post-0.9).
  Nothing is harvested into it any more; a done item stays in its own file as `[x]`.
- [`docs/SESSIONS.md`](../SESSIONS.md) — append-only session log; read the tail at session start, append an
  entry before finishing.
- [`docs/decisions/`](../decisions/) — ADRs: decisions where a plausible alternative was rejected or a design
  rests on evidence (e.g. why a fake is *not* inferred from TRAN_SPEED).
- [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) — the gather→compute→render shape and the two fake-detection
  strategies.
- [`docs/MODEL-ECONOMICS.md`](../MODEL-ECONOMICS.md) — which model does what, and session/token hygiene.
- [`CHANGELOG.md`](../../CHANGELOG.md) — user-facing change history.

Done through 0.9 (packaging, native benchmark, capacity sweep, CSD decode + cross-checks, SQLite history, latency
percentiles, the test suite) plus the post-0.9 macOS/CSD work lives in `docs/ROADMAP-DONE.md`. The bash original
(`archive/rpi-sdinfo.sh`) is reference only, not developed further.
