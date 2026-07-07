# 0002 — Relicence to Apache-2.0

**Status**: accepted • **Date**: 2026-07-06 (commit `2e4ed88`)

## Context

The repo carried an inconsistent licence: `LICENSE` was GPL-2.0 and `pyproject.toml` followed it
(`GPL-2.0-or-later`), while the per-file header comments said "GNU GPL v3". That contradiction had to be
resolved before any public release — three sources disagreeing is a legal ambiguity, not a cosmetic one.

## Decision

Relicence the whole project to **Apache-2.0**, made consistent across `LICENSE`, `pyproject.toml`
(`license = { text = "Apache-2.0" }` + the OSI classifier) and every per-file header. This was Mike's call as
the owner.

## Rejected

- **Pick one of the GPL versions (v2 or v3) and make the three sources agree.** A copyleft licence is a heavier
  obligation than this small, dependency-free utility warrants, and Apache-2.0 lets it be embedded, packaged and
  redistributed (including into other tooling) with minimal friction — the point of a widely-useful sanity-check
  tool. Apache-2.0 also carries an explicit patent grant, which GPL-2.0 lacks.

## Consequences

- `CONTRIBUTING.md` states contributions are under Apache-2.0.
- Any new source file gets the Apache-2.0 header, not a GPL one.
- The earlier "resolve the licence inconsistency" roadmap blocker is closed.
