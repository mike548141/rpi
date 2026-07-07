# rpi
Raspberry Pi tools

If I make more tools then I will add them here, but currently this is just one tool called rpi-sdinfo.

## rpi-sdinfo
A tool to (a) test the performance and integrity of SD/MMC cards, and (b) try to spot genuine vs fake cards by
comparing what the card reports about itself against how it actually performs. Originally written in bash
(`archive/rpi-sdinfo.sh`, kept for reference only); the developed version is the pure-Python `rpi_sdinfo` package,
installable as the `rpi-sdinfo` command (see [Install](#install)). Still short of a tagged v1.0, but a solid,
working start.

If it proves useful the plan is a public service where everyone can share results to build a database of SD card
identifiers, performance, and failure rates.

### What it does

- Identifies the card: capacity, and on a Raspberry Pi the make / model / branding decoded from the CID/CSD
  registers, plus filesystem and IO statistics.
- Benchmarks it with a **native, dependency-free** engine (the `rpi-sdbench` tool) — sequential write throughput
  and random 4 KiB read/write IOPS. No `fio` (or any external tool) required.
- Grades the measured performance against the card's rated speed class, falling back to **A1** (the Raspberry Pi
  baseline) when the class is unknown. Prints PASS/FAIL per metric and exits non-zero on failure, so it is usable
  in scripts.
- **Unmasks fake cards** two ways (native `rpi-sdverify`, the pure-Python cousin of `f3` / `h2testw`):
  - **Thorough, non-destructive** (`--capacity-check`): fills the card's free space with offset-stamped data
    and reads it all back. A counterfeit that reports a huge size but has a small chip fails verification at its
    true capacity. Only adds its own test files and deletes them again.
  - **Quick, destructive corners sweep** (`rpi-sdverify --device …`): probes block 0, every power-of-two offset,
    and the last block of the *reported* capacity. A fake truncates the block address at a power-of-two
    boundary, so block 0 and that boundary alias onto one physical cell — guaranteeing detection in ~log₂(N)
    probes (29 for a 512 GB card) instead of writing the whole card. Writes the raw device, so it is gated
    behind `--yes` and refuses a mounted device.
- **Cross-checks the card's own story** (Raspberry Pi only, instant, no writes). Decodes the CSD register
  (SDSC/SDHC/SDXC/SDUC capacity, bus speed, command classes) and flags internal contradictions — above all a
  Standard-Capacity CSD on a card claiming tens of GB, which is impossible per the SD spec and the tell-tale of
  a small card reflashed to lie. Also warns on a CSD-vs-reported capacity mismatch or a future manufacturing
  date. Shown as a `CONSISTENCY` section; a hard contradiction fails the exit code.
- **Reads nicely, scripts cleanly.** A colourful, sectioned terminal report for humans (with a live progress
  spinner during the benchmark), and `--format json` for other software — the JSON document is the *only* thing
  on stdout, so `rpi-sdinfo --json | jq` just works.

### Platforms

- **Raspberry Pi Linux** — full detail (reads the SD CID/CSD registers from sysfs). Run with `sudo` so it can
  read every register. No packages to install.
- **macOS** — plug the card into a reader and just run `rpi-sdinfo`: with no `--device`/`--dir` it auto-detects
  the inserted removable card (preferring an SD-bus reader) and benchmarks that card rather than the boot disk.
  Identity is otherwise limited to what macOS exposes via `diskutil` (capacity, media name, bus, SMART,
  removable) because macOS does not expose the SD CID/CSD registers — though on a Mac with a **built-in SD slot**
  the tool also asks the card reader for the card's own product/make/serial. The benchmark and grading work
  normally. Pass `--dir /Volumes/MYCARD` (or `--device disk4`) to target a specific card.
- **Windows** — plug the card into a reader. Identity is limited to the drive's capacity, volume label and
  removable flag (Windows does not expose the SD CID/CSD registers either); the benchmark and grading work
  normally. Point `--dir` at the card's drive, e.g. `--dir E:\`.

Only the Python standard library is used — there are **no runtime dependencies** to `pip install` on any platform.

### Install

The recommended way is [`pipx`](https://pipx.pypa.io) (installs into an isolated environment and puts the
commands on your `PATH`):

```
pipx install rpi-sdinfo          # once published to PyPI
# or straight from the repo:
pipx install git+https://github.com/mike548141/rpi
```

Or with plain `pip` (ideally in a virtualenv):

```
pip install rpi-sdinfo
```

This installs three commands — `rpi-sdinfo` (the full tool), `rpi-sdbench` (benchmark only) and `rpi-sdverify`
(capacity-fraud sweep only). No install needed to try it from a clone — run the package directly:

```
git clone https://github.com/mike548141/rpi && cd rpi
python3 -m rpi_sdinfo --help        # requires src/ on the path: see below
PYTHONPATH=src python3 -m rpi_sdinfo --no-benchmark
```

(Once installed, drop the `PYTHONPATH=src` prefix — `rpi-sdinfo` / `python -m rpi_sdinfo` just work.)

### Usage

Examples use the installed `rpi-sdinfo` command; `python -m rpi_sdinfo` is equivalent everywhere.

```
# Raspberry Pi (full detail; sudo to read the registers)
sudo rpi-sdinfo

# macOS (benchmark + whatever identity the reader exposes)
rpi-sdinfo --dir /Volumes/MYCARD

# Windows (from PowerShell / cmd)
rpi-sdinfo --dir E:\

# Just the card detail, no benchmark
rpi-sdinfo --no-benchmark

# Machine-readable output for other tools / scripts
rpi-sdinfo --json --dir /Volumes/MYCARD | jq .grade.pass

# Just an exit code (0 = PASS, 1 = FAIL) for automation
rpi-sdinfo --quiet --dir /Volumes/MYCARD; echo $?

# Unmask a fake card: fill it, write + verify the whole capacity (slow; adds flash wear)
rpi-sdinfo --dir /Volumes/MYCARD --capacity-check

# Save every run to a local SQLite history (default ~/.rpi-sdinfo/results.db; pass a path to override)
rpi-sdinfo --dir /Volumes/MYCARD --save-db

# Summarise that history (every card tested, verdicts, and the fakes flagged) without testing a card
rpi-sdinfo --db-query

# Dump the verbatim sources (dumpe2fs / registers / decoded CSD / raw samples) when a field looks wrong
sudo rpi-sdinfo --raw

# Just a native benchmark of a path, standalone
rpi-sdbench --dir /Volumes/MYCARD

# Just a native capacity-fraud sweep of a path, standalone (non-destructive, fills free space)
rpi-sdverify --dir /Volumes/MYCARD

# Quick fake sniff of a raw device (DESTRUCTIVE: overwrites the card; unmount it first)
rpi-sdverify --device /dev/disk4 --yes
```

Useful options: `--device`, `--partition`, `--dir`, `--runs`, `--size-mb`, `--seconds`, `--no-benchmark`,
`--capacity-check`, `--capacity-mb`, `--yes`, `--format text|json` (or `--json`), `--quiet`, `--raw`,
`--save-db [PATH]`, `--db-query [PATH]`, `--color`/`--no-color`, `--version` (`--help` for the full list). Colour follows the
[`NO_COLOR`](https://no-color.org) and `CLICOLOR_FORCE` conventions and switches itself off when output is piped
or redirected.

The capacity sweep is **opt-in and gated**: it fills the card's free space and writes its whole capacity once,
so it asks for confirmation first (or pass `--yes`; `--yes` is required when non-interactive, e.g. with `--json`
or `--quiet`). Cap it to a quick partial check with `--capacity-mb N`. A safety margin of free space is always
left, so the filesystem is never wedged.

**Exit codes** (so it drops into scripts and CI): `0` card passed every test it ran (or run with
`--no-benchmark` and no `--capacity-check`), `1` card failed a test (too slow for its grade, smaller than it
reports, or an impossible CSD/CID self-declaration), `2` usage error or unsupported platform.

### For other software (the JSON contract)

`--format json` emits one document on stdout: `schema` (`rpi-sdinfo/1`), `tool_version`, `generated` (UTC
ISO-8601), then `platform`, `device`, `hardware`, `software`, `storage`, and — on Linux — `filesystem` and
`stats`; plus `benchmark` (every per-run sample) and `grade` (per-metric measured/target/pass and the overall
`grade.pass`). With `--capacity-check --yes` it also carries `capacity` (swept/verified byte counts, the first
bad offset if any, a usable-capacity estimate, and `capacity.ok`). On a Raspberry Pi it carries `consistency`
(`findings` with per-issue severity, and `consistency.ok`) plus the decoded CSD under `storage.csd_decoded`.
Progress and any messages go to stderr, never stdout. `SCHEMA` is bumped only on a breaking change to the shape, so consumers can pin to it. `sdbench.py
--json` and `sdverify.py --json` each emit their own standalone JSON.

Add `--raw` for a `raw` block carrying the verbatim sources (full `dumpe2fs` / `diskutil` record, raw
`/proc` reads) alongside the decoded CSD and every per-run benchmark sample — off by default so the contract
above stays clean.

### Building a history (`--save-db`)

`--save-db [PATH]` appends each run to a local SQLite database (default `~/.rpi-sdinfo/results.db`), created on
first use. One row per run: the full JSON document verbatim in a `document` column, plus typed columns you can
query directly — identity (`card_label`, `manufacturer`, `cid_psn`), `capacity_gb`, measured performance
(`seq_write_mbps`, `rand_write_iops`, `rand_read_iops`), `csd_capacity_type`, and the pass/fail flags
(`grade_pass`, `capacity_ok`, `consistency_ok`, `overall_pass`). So `SELECT card_label, overall_pass FROM runs
WHERE overall_pass = 0` lists every card that failed a test. The DB is **local-only** and keeps the real
serial/MACs; a save failure warns but never changes the exit code. It's the seed of the crowd-sourced card
database on the roadmap — sharing it needs a stronger anonymisation scheme first.

Read it back with `--db-query` (no card needed): totals, a per-card table (grouped by label + CID serial, with
run count, latest verdict, best sequential write and rated class), and every flagged run with a plain-English
reason. `--db-query --json` emits the same summary as one document for scripting. The benchmark also records the
full latency distribution (mean, p50/p95/p99, min/max in ms) per phase — shown by `rpi-sdbench` directly, carried
in the JSON `benchmark` block, and dumped by `--raw` — because the tail latency is what a worn or fake card
betrays even when its mean looks fine.

### Testing

A dependency-free `unittest` suite lives in `tests/` and runs anywhere Python 3.6+ does — no SD card or Pi
required, because it covers the hardware-independent logic (CSD decode + fake-detection cross-checks, capacity
and grade maths, latency percentiles, the capacity-sweep pattern and corners-alias catch) plus an end-to-end
CLI smoke test that drives the real `sdbench`/`sdverify` write-and-verify paths against a scratch file:

```bash
python3 -m unittest discover -s tests             # run everything (~3 s)
python3 -m unittest discover -s tests -v          # verbose, per-test
cd tests && python3 -m unittest test_csd          # one module
```

What the suite can't cover is the Linux sysfs/`dumpe2fs`/`diskstats` reads in `gather_linux()` — those need
real Pi hardware (see [ROADMAP.md](ROADMAP.md)).

### More

- [SD_CARDS.md](SD_CARDS.md) — how SD cards identify themselves (CID), how to read the label's class symbols,
  what performance each class promises, and how to spot fakes.
- [ROADMAP.md](ROADMAP.md) — what's done and what's planned before v1.0, including Pi hardware testing and a
  counterfeit-capacity (write/verify) test.

### Scope & expectations

**What it is:** a zero-dependency, cross-platform *sanity check* for SD/MMC cards — identity, a quick
benchmark, capacity-fraud detection, and instant metadata cross-checks, all in one command with nothing to
install. The niche it serves is the Raspberry Pi / homelab / secondhand-card crowd who want one tool that
answers "is this card genuine, and is it fast enough?".

**What it is not:** a certified benchmark or a forensic capacity tester. It does not try to out-do the
specialists at their one job — [`f3`](https://github.com/AltraMayor/f3) / h2testw for exhaustive capacity
fraud, `smartctl` for SMART, `fio` for rigorous throughput. Its value is *breadth in a single portable
command* plus the CSD-metadata liar-detection those tools don't do. For a definitive verdict on a suspect
card, confirm with a full `f3` sweep.

**Honest limitations (as of 0.9):**

- The **Raspberry Pi path is not yet hardware-tested** — the macOS path is exercised end-to-end and unit-tested,
  the Windows path is written to the same stdlib shape but unrun on real hardware, and the Linux `gather_linux()`
  sysfs reads are carried over from the working bash logic and compile, but need a run on a real Pi before v1.0.
- **Grading is heuristic** (median-of-best-half vs the rated class, A1 fallback), not a spec-compliant SD
  Association test.
- The **crowd-sourced upload / shared database is unsolved** — it needs a stronger anonymisation scheme than a
  fixed-salt hash over a low-entropy serial before any result leaves your machine.

See [ROADMAP.md](ROADMAP.md) for the full status and the path to v1.0.
