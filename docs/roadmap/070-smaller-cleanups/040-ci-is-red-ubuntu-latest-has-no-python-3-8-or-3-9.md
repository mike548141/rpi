- [ ] **CI is red: `ubuntu-latest` no longer provides Python 3.8 or 3.9.**
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
