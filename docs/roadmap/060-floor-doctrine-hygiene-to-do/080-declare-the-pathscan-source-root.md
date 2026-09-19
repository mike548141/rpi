- [ ] **Declare this repo's `pathscan` source root once atelier ships the
      setting** — queued here from atelier on Mike's ruling, 2026-09-19
      (atelier board `320/010`): *"The declared per repo option but we make
      those repos add them by putting the work on their boards"*.
      This repo keeps its code under `src/rpi_sdinfo/`, and prose naturally names
      modules relative to it (`sub/module.py`). `pathscan` resolves only from
      the repo root, the file's own folder and `docs/`, so those references
      show as missing — false warnings. Atelier is adding a per-repo list of
      extra resolution roots in `.atelier-floor.json`.
      **Blocked on:** atelier `320/010` part (1) landing, then a pin bump here.
      **Then:** add `src/rpi_sdinfo` as this repo's declared root, run `pathscan` and
      record the before/after warning counts in this item.
      Atelier is also weighing whether `pathscan` should block rather than warn
      (`320/310`), so clearing this repo's residue first matters.
