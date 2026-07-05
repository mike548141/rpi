# rpi
Raspberry Pi tools

If I make more tools then I will add them here, but currently this is just one tool called rpi-sdinfo.

## rpi-sdinfo
A tool to (a) test the performance and integrity of SD/MMC cards, and (b) try to spot genuine vs fake cards by
comparing what the card reports about itself against how it actually performs. Originally written in bash
(`archive/rpi-sdinfo.sh`, kept for reference only); the developed version is `rpi-sdinfo.py`. Still short of a tagged
v1.0, but a solid, working start.

If it proves useful the plan is a public service where everyone can share results to build a database of SD card
identifiers, performance, and failure rates.

### What it does

- Identifies the card: capacity, and on a Raspberry Pi the make / model / branding decoded from the CID/CSD
  registers, plus filesystem and IO statistics.
- Benchmarks it with a **native, dependency-free** engine (`sdbench.py`) — sequential write throughput and
  random 4 KiB read/write IOPS. No `fio` (or any external tool) required.
- Grades the measured performance against the card's rated speed class, falling back to **A1** (the Raspberry Pi
  baseline) when the class is unknown. Prints PASS/FAIL per metric and exits non-zero on failure, so it is usable
  in scripts.
- **Unmasks fake cards** two ways (native `sdverify.py`, the pure-Python cousin of `f3` / `h2testw`):
  - **Thorough, non-destructive** (`--capacity-check`): fills the card's free space with offset-stamped data
    and reads it all back. A counterfeit that reports a huge size but has a small chip fails verification at its
    true capacity. Only adds its own test files and deletes them again.
  - **Quick, destructive corners sweep** (`sdverify.py --device …`): probes block 0, every power-of-two offset,
    and the last block of the *reported* capacity. A fake truncates the block address at a power-of-two
    boundary, so block 0 and that boundary alias onto one physical cell — guaranteeing detection in ~log₂(N)
    probes (29 for a 512 GB card) instead of writing the whole card. Writes the raw device, so it is gated
    behind `--yes` and refuses a mounted device.
- **Reads nicely, scripts cleanly.** A colourful, sectioned terminal report for humans (with a live progress
  spinner during the benchmark), and `--format json` for other software — the JSON document is the *only* thing
  on stdout, so `rpi-sdinfo --json | jq` just works.

### Platforms

- **Raspberry Pi Linux** — full detail (reads the SD CID/CSD registers from sysfs). Run with `sudo` so it can
  read every register. No packages to install.
- **macOS** — plug the card into a reader. Identity is limited to what macOS exposes via `diskutil` (capacity,
  media name, bus, SMART, removable) because macOS does not expose the SD CID/CSD registers; the benchmark and
  grading work normally. Point `--dir` at the mounted card, e.g. `/Volumes/MYCARD`.
- **Windows** — plug the card into a reader. Identity is limited to the drive's capacity, volume label and
  removable flag (Windows does not expose the SD CID/CSD registers either); the benchmark and grading work
  normally. Point `--dir` at the card's drive, e.g. `--dir E:\`.

Only the Python standard library is used — nothing to `pip install` on any platform.

### Usage

```
# Raspberry Pi (full detail; sudo to read the registers)
sudo ./rpi-sdinfo.py

# macOS (benchmark + whatever identity the reader exposes)
./rpi-sdinfo.py --dir /Volumes/MYCARD

# Windows (from PowerShell / cmd)
python rpi-sdinfo.py --dir E:\

# Just the card detail, no benchmark
./rpi-sdinfo.py --no-benchmark

# Machine-readable output for other tools / scripts
./rpi-sdinfo.py --json --dir /Volumes/MYCARD | jq .grade.pass

# Just an exit code (0 = PASS, 1 = FAIL) for automation
./rpi-sdinfo.py --quiet --dir /Volumes/MYCARD; echo $?

# Unmask a fake card: fill it, write + verify the whole capacity (slow; adds flash wear)
./rpi-sdinfo.py --dir /Volumes/MYCARD --capacity-check

# Just a native benchmark of a path, standalone
./sdbench.py --dir /Volumes/MYCARD

# Just a native capacity-fraud sweep of a path, standalone (non-destructive, fills free space)
./sdverify.py --dir /Volumes/MYCARD

# Quick fake sniff of a raw device (DESTRUCTIVE: overwrites the card; unmount it first)
./sdverify.py --device /dev/disk4 --yes
```

Useful options: `--device`, `--partition`, `--dir`, `--runs`, `--size-mb`, `--seconds`, `--no-benchmark`,
`--capacity-check`, `--capacity-mb`, `--yes`, `--format text|json` (or `--json`), `--quiet`,
`--color`/`--no-color`, `--version` (`--help` for the full list). Colour follows the
[`NO_COLOR`](https://no-color.org) and `CLICOLOR_FORCE` conventions and switches itself off when output is piped
or redirected.

The capacity sweep is **opt-in and gated**: it fills the card's free space and writes its whole capacity once,
so it asks for confirmation first (or pass `--yes`; `--yes` is required when non-interactive, e.g. with `--json`
or `--quiet`). Cap it to a quick partial check with `--capacity-mb N`. A safety margin of free space is always
left, so the filesystem is never wedged.

**Exit codes** (so it drops into scripts and CI): `0` card passed every test it ran (or run with
`--no-benchmark` and no `--capacity-check`), `1` card failed a test (too slow for its grade, or smaller than it
reports), `2` usage error or unsupported platform.

### For other software (the JSON contract)

`--format json` emits one document on stdout: `schema` (`rpi-sdinfo/1`), `tool_version`, `generated` (UTC
ISO-8601), then `platform`, `device`, `hardware`, `software`, `storage`, and — on Linux — `filesystem` and
`stats`; plus `benchmark` (every per-run sample) and `grade` (per-metric measured/target/pass and the overall
`grade.pass`). With `--capacity-check --yes` it also carries `capacity` (swept/verified byte counts, the first
bad offset if any, a usable-capacity estimate, and `capacity.ok`). Progress and any messages go to stderr, never
stdout. `SCHEMA` is bumped only on a breaking change to the shape, so consumers can pin to it. `sdbench.py
--json` and `sdverify.py --json` each emit their own standalone JSON.

### More

- [SD_CARDS.md](SD_CARDS.md) — how SD cards identify themselves (CID), how to read the label's class symbols,
  what performance each class promises, and how to spot fakes.
- [ROADMAP.md](ROADMAP.md) — what's done and what's planned before v1.0, including Pi hardware testing and a
  counterfeit-capacity (write/verify) test.

> **Status:** the macOS path is tested end-to-end; the Windows path is written to the same stdlib-only shape but
> not yet run on real Windows hardware; the Raspberry Pi path is carried over from the working bash logic and
> compiles, but still needs a run on real Pi hardware before v1.0.
