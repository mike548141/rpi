- [x] **CI is red: `ubuntu-latest` no longer provides Python 3.8 or 3.9.**
      Found 2026-11-12 by a parent-repo session probing the fleet; queued here,
      not fixed from there. The `CI` workflow has failed on every push since at
      least 2026-11-01. `ubuntu-latest` now resolves to Ubuntu 26.04, and
      `actions/setup-python` has no 3.8 or 3.9 build for it, so those two matrix
      entries die at "Set up Python" with "version not found". The tests never
      run, so this says nothing about the code. The `floor` workflow is green.
      **Shapes to weigh:** pin the low-floor entries to an older runner image
      that still carries those versions (`ubuntu-22.04`), or raise the declared
      Python floor and drop them. The second changes what the package promises
      users, so it needs the principal's word.
      **Done means** the `CI` workflow is green on `main`, and the README's
      supported versions match the matrix.
      **Fix landed 2026-11-13** (shape one, no change to what the package promises):
      the 3.8 and 3.9 Linux entries run on `ubuntu-22.04`; `ubuntu-latest` keeps 3.11
      and 3.13. The README and `pyproject.toml` still say 3.6+ with CI flooring at
      3.8, which the matrix still matches. Flips to `[x]` once `CI` is green at the
      pushed head.
      **Done 2026-11-13:** `CI` green at `013f41b`, all eleven jobs, including
      `ubuntu-22.04` py3.8 and py3.9
      ([run 43378313548](https://github.com/mike548141/rpi/actions/runs/43378313548)).
