# 2026-08-17 (cont.) — The pin moved twice

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 43+1 -->
- [2026-08-17 (cont.) · The pin moved twice](2026-08-17-0952-pin-moved-twice.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `38016b6`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-08-17 (cont.)** — **The pin moved twice, and the second bump was the interesting one.** Mike asked to
  confirm the pin bump; re-running the drift check found atelier had landed **28 further commits while the
  board split was being built** — so `2428fdf`, chosen a few hours earlier, was already stale. Bumped again to
  `0af3006` after reading the three that touch `docs/method/`. 🔎 Two of them changed text this repo *inlines*,
  which is the retrofit class the 2026-07-30 bump found and nothing yet watches: (a) the **Three Laws are gone
  from the house apex** (2026-08-15) — the principal's authority stands in their place, absolute and
  never-decaying, and at the always-confirm floor an under-briefed approval is **re-briefed before** the
  irreversible action rather than challenged after it; (b) the **channel** landed as a concurrency primitive
  (announce your file set on open; a message reserves nothing, only a pushed artefact does; the shared index and
  mid-rebase state are shared surfaces). Both retrofitted. The inlined block now diffs against
  `../atelier/docs/method/PROPAGATION.md`'s canonical one at exactly two places: the pin SHA, and this repo's own
  added sentence about the close carrying the *pushed* floor run's result — a child addition, which propagation
  doctrine allows.
  ⚠️ Worth naming for the next session: my first bump was **correct when made and stale within the hour**. A pin
  is a point-in-time claim about a moving parent, and reading the drift *once* at session open is not the same
  as it holding at session close. Re-run the drift check at close, not only at open. Also unchanged: stampscan —
  the scanner built to catch exactly this inline-copy drift — is still deliberately unwired, so every retrofit
  here is found by hand or not at all.
  🎯 **Left for Mike, deliberately not done**: atelier's own board carries the fleet-rollout item
  (`010-…/030-fleet-rollout-of-the-split-board.md`) listing `ros`, `shed` and `faves` and reading "gated on this
  cycle's review closing". rpi has now rolled out ahead of that gate on Mike's instruction, but recording that
  fact belongs on atelier's board, and writing to another repo's queue from this session was not asked for.
