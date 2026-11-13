# 2026-07-11 — Adopted into the atelier fleet

> Moved word for word from `docs/SESSIONS.md` on 2026-11-13, when the log
> split into an index and one detail file per entry. The file name's date
> and time are the UTC time of commit `5b5ffcb`, which first landed this entry;
> the entry's own date is the writer's local date, up to a day ahead of UTC.
> Nothing in it changed.

- **2026-07-11** — **Adopted into the atelier fleet** (standardise-existing pass,
  pinned `atelier@1588fda`). Prepended the inherited **doctrine block** (apex +
  always-confirm floor + drift check) above the existing onramp; added the
  scanner-floor CI (`.github/workflows/floor.yml`, atelier's public tools run as
  a sibling on every push/PR) and installed the fail-closed pre-commit hook
  (`hooks.atelierTools` → `../atelier/tools`, proven blocking a planted key).
  No other change — rpi was already close to the house standard. Tree scanned
  clean. Next: the crowd-upload anonymisation decision (unchanged).
