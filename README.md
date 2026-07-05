# rpi
Raspberry Pi tools

If I make more tools then I will add them here, but currently this is just one tool called rpi-sdinfo.

## rpi-sdinfo
A tool to (a) test the performance and integrity of SD/MMC cards, and (b) try to spot genuine vs fake cards by
comparing what the card reports about itself against how it actually performs. Originally written in bash
(`rpi-sdinfo.sh`, kept for reference only); the developed version is `rpi-sdinfo.py`. Still short of a tagged
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

### Platforms

- **Raspberry Pi Linux** — full detail (reads the SD CID/CSD registers from sysfs). Run with `sudo` so it can
  read every register. No packages to install.
- **macOS** — plug the card into a reader. Identity is limited to what macOS exposes via `diskutil` (capacity,
  media name, bus, SMART, removable) because macOS does not expose the SD CID/CSD registers; the benchmark and
  grading work normally. Point `--dir` at the mounted card, e.g. `/Volumes/MYCARD`.

### Usage

```
# Raspberry Pi (full detail; sudo to read the registers)
sudo ./rpi-sdinfo.py

# macOS (benchmark + whatever identity the reader exposes)
./rpi-sdinfo.py --dir /Volumes/MYCARD

# Just the card detail, no benchmark
./rpi-sdinfo.py --no-benchmark

# Just a native benchmark of a path, standalone
./sdbench.py --dir /Volumes/MYCARD
```

Useful options: `--device`, `--partition`, `--dir`, `--runs`, `--size-mb`, `--seconds`, `--no-benchmark`
(`--help` for the full list).

### More

- [SD_CARDS.md](SD_CARDS.md) — how SD cards identify themselves (CID), how to read the label's class symbols,
  what performance each class promises, and how to spot fakes.
- [ROADMAP.md](ROADMAP.md) — what's done and what's planned before v1.0, including Pi hardware testing and a
  counterfeit-capacity (write/verify) test.

> **Status:** the macOS path is tested end-to-end; the Raspberry Pi path is carried over from the working bash
> logic and compiles, but still needs a run on real Pi hardware before v1.0.
