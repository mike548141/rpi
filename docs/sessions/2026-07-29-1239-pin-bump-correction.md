# 2026-07-30 (cont.) — Correction to the pin-bump entry

**From the retired session log**, word for word; only its link paths were re-pointed for this folder:

<!-- archivecut:log-entry docs/SESSIONS.md 40+1 -->
- [2026-07-30 (cont.) · Correction to the pin-bump entry](2026-07-29-1239-pin-bump-correction.md)


> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `0237ac9`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-30 (cont.)** — **Correction to the entry above, found by the floor run that followed it.** The
  wrapscan declaration I had just written gave as its reason "new prose is written at the house width" — and
  the session entry immediately above it added **35 more over-width lines** (716 → 751) before the commit
  finished. The reason was false the moment it was committed. 🔎 The real finding underneath: this repo's prose
  is written at ~110 columns *everywhere*, in every doc, not as accumulated sloppiness in a few frozen files.
  So it is a **style mismatch spanning the corpus**, not a debt to be worked down — and rewrapping one entry to
  85 while 344 lines around it sit at 110 would read worse, not better. The declaration and the roadmap item
  are corrected to say that, and to name the two honest resolutions the review must choose between: adopt 85
  for new prose and glob the frozen records, or exempt this repo's prose from the house width and say so. What
  I got wrong was not the measurement but the *diagnosis* — I read a corpus-wide convention as a backlog, which
  is the same shape as the ~40-vs-716 error it sat next to.
