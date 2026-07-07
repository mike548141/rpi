# Model & token economics — working policy

How to split work between Claude models on this repo, and how to keep sessions token-efficient. Adapted
2026-07-08 from the sibling `ros`/`tiki` policy. Prices are public API list prices — re-check them if this is
more than a few months old.

## The two billing pools

| Pool | Models | Marginal cost of a token |
|---|---|---|
| Plan-included | Opus 4.8 (and Sonnet/Haiku) | Zero dollars, but draws down plan usage limits |
| Usage-billed | Fable 5 | Real money: $10/M input, $50/M output (thinking bills as output and is always on) |

Reference prices (per M tokens, in/out): Fable 5 $10/$50 · Opus 4.8 $5/$25 · Sonnet 5 $3/$15 · Haiku 4.5 $1/$5.
Cache reads ≈ 0.1× input price; cache writes ≈ 1.25× (5-minute TTL).

## Who does what

- **Opus 4.8 (plan)** — the workhorse. Building, iterating, tests, docs, exploration, long agentic sessions,
  anything mechanical or high-volume. Burning plan quota on exploration is fine; burning Fable dollars on it is
  not. All the work to date has been Opus.
- **Fable 5 (usage-billed)** — the reviewer and hard-problem solver: code/doc/approach review, and debugging
  Opus is stuck on. **Keep Fable sessions short and pre-scoped** — hand it the commit range / diff / specific
  files, not the repo; ask for findings, not rewrites, and apply fixes back on Opus. A scoped review (~100k in,
  ~20k out) ≈ $2; an unscoped repo-walk costs several times that for no extra insight.
  - Unlike `ros` (where live-network changes must be Fable-reviewed before they are trusted), rpi has **no
    live-hardware risk**, so review is *available, not mandated*. Where it earns its cost here: the
    `gather_linux()` / `sdbench` Linux path that **cannot be run in this dev environment** (no Pi) — careful
    review of logic that can't be executed is worth more than review of code the tests already exercise. The
    `/code-review ultra` cloud path is the built-in, user-triggered way to get that (it is billed and cannot be
    launched autonomously).
- **Subagents (Explore, etc.)** — use them from either model for fan-out reading/searching so the expensive
  main context stays small. Matters most in Fable sessions.

## Session hygiene (both models)

1. **One task per session.** Context is resent (cached) each turn; a pivoted session drags the old task's
   tokens along. Wrap up (append to `docs/SESSIONS.md`), start fresh.
2. **Never switch model mid-session.** The prompt cache is per-model — a switch re-processes the whole context
   at full input price and loses thinking continuity. Switch at session boundaries.
3. **Cache TTL is 5 minutes.** During active work, gaps longer than that re-write the cache (full input
   re-read). Matters most on usage-billed sessions; on plan it just wastes quota.
4. **Watch context growth.** Long sessions get slower and costlier per turn. When a session feels long, append
   the SESSIONS.md entry and restart.
5. **Heavy skills are episodic costs.** A skill invocation (e.g. the claude-api reference) can inject 50–100k
   tokens. Fine when needed; don't invoke speculatively, especially in Fable sessions.
6. **Point, don't paste.** Give file paths and line ranges rather than pasting large content the model can read
   itself — reads are targeted; pastes live in context forever.

## Fixed per-session overhead (measured 2026-07-08)

A session starts by loading: system prompt + tools (~15–20k tokens), the global + project `CLAUDE.md` (~2.5k
combined), the memory index (small), and — on demand — `ROADMAP.md` (~1.9k), the `docs/SESSIONS.md` tail
(~0.7k) and `docs/ARCHITECTURE.md` (~1.5k). Roughly **~22–27k tokens before any work happens**, of which only
~6k is repo docs we control; the rest is the fixed harness.

`ROADMAP.md` was split on 2026-07-08 (it had accumulated the full 0.3→0.9 version history, ~5k+ tokens) into
the lean roadmap + `docs/ROADMAP-DONE.md` (completed detail) + `docs/SESSIONS.md` (append-only log, tail-read
only). Keep it that way: **bulk that isn't needed every session — session-log entries, completed-work detail —
does not accumulate in the every-session read path.** The lean-roadmap rule is about *where* information lives,
not deleting it; never sacrifice clarity to hit a number (the cost is linear, not a cliff).

## Rules of thumb

- 4 characters ≈ 1 token; 1 KB ≈ 250 tokens.
- Fable output (incl. thinking) is 5× Fable input — keep a Fable session cheap by asking narrow questions of a
  lean context.
- VS Code vs terminal makes no difference to token economics; the levers are session scope, context size, and
  model choice.
