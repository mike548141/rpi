# 0001 — Standard library only, zero runtime dependencies

**Status**: accepted • **Date**: 2026-07-08 (documenting a founding constraint)

## Context

`rpi-sdinfo` is meant to be run on whatever machine has the card reader — most often a Raspberry Pi flashed
with a stock OS image, sometimes a locked-down macOS or Windows box. The people who need it most (someone who
just bought a suspiciously cheap "1 TB" card) are the least likely to want to set up a virtualenv and install a
dependency tree, and a Pi Zero has little room or patience for one. The tool also shells out to and competes
with `f3` / h2testw / `smartctl`, all of which are a separate install.

## Decision

The tool depends on the Python **standard library only** — zero runtime dependencies — and holds a **Python
3.6+** floor. It must run on stock Pi OS / macOS / Windows Python with nothing to `pip install`. Where the
stdlib lacks something (percentiles, cache-bypassing IO), we hand-roll it rather than add a dependency. Dev-only
tooling (e.g. `ruff`) is allowed because it never ships in the wheel and never runs on a user's machine.

## Rejected

- **Pull in a benchmark/IO or table-rendering library.** Faster to write, but it turns a one-command sanity
  check into an install exercise for exactly the audience least able to do it, and risks a wheel that won't
  build on an old Pi.
- **Raise the floor to a modern Python** for niceties like `statistics.quantiles`. Rejected while real Pi OS
  images still ship older interpreters; the hand-rolled helper is a few lines.

## Consequences

- New code reaches for the stdlib first; a proposed runtime dependency is a design change, not a detail.
- Some code is more verbose than it would be with a helper library (the percentile helper, the ANSI/UI layer,
  the Win32 `ctypes` calls). That is the accepted cost.
- CI installs the package with no runtime deps and byte-compiles it; the only extra is dev tooling.
- See [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) for how this shapes the module layout.
