#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.1-20260705
# File:         sdbench.py
# License:      GNU GPL v3
# Language:     Python 3.6 or later
# Source:       https://github.com/mike548141/rpi
#
# Description:
#   A small, dependency-free storage benchmark that replaces the external `fio` tool used by rpi-sdinfo.
#   It emulates the SD Association Application Performance Class 1 (A1) sniff test: sequential write
#   throughput, plus random 4 KiB write and read IOPS. Pure Python standard library only, so it runs on
#   Raspberry Pi Linux and macOS (and anywhere else CPython does) with nothing to install.
#
#   This is a sniff test, not a certified benchmark. The card is not put into the fresh, aligned state the
#   SD specification requires, and without kernel O_DIRECT we lean on cache-bypassing hints instead:
#     * macOS  - F_NOCACHE on the file descriptor (fcntl) so IO bypasses the unified buffer cache.
#     * Linux  - O_DSYNC on writes (each write reaches the device) and posix_fadvise(DONTNEED) before reads
#                so reads miss the page cache. Falls back to a final fsync() where those are unavailable.
#   The numbers are good enough to tell a genuine class-10/A1 card from a slow or counterfeit one, which is
#   all rpi-sdinfo needs. See ROADMAP.md for the path to O_DIRECT and a capacity-fraud sweep.
#
# Usage (standalone):
#   python3 sdbench.py [--dir /var/tmp] [--runs 3] [--size-mb 64] [--seconds 10]
#   The test file is created in --dir (default the system temp dir) and removed afterwards. Point --dir at a
#   path on the card you want to test.

import argparse
import os
import random
import statistics
import sys
import tempfile
import time

# fcntl is POSIX only (Linux, macOS); guard so an import never hard-fails the module on other platforms
try:
  import fcntl
except ImportError:
  fcntl = None

# macOS fcntl command to disable the unified buffer cache for a file descriptor (from <sys/fcntl.h>)
F_NOCACHE = 48

# Default benchmark shape, chosen to mirror the fio job rpi-sdinfo previously used
DEFAULT_SIZE_MB = 64        # Size of the test file, and the sequential write payload
DEFAULT_SECONDS = 10        # Duration of each random IO test
DEFAULT_RUNS = 3            # Repeat the whole benchmark this many times to average out noise
SEQ_BLOCK = 512 * 1024      # 512 KiB sequential write block, as per the A1 test
RAND_BLOCK = 4 * 1024       # 4 KiB random IO block, as per the A1 test

#======================================
# Low level, cache-bypassing IO helpers
#--------------------------------------

def _disable_cache(file_descriptor):
  # On macOS, ask the kernel to bypass the buffer cache for this descriptor so we measure the device, not RAM
  if sys.platform == 'darwin' and fcntl is not None:
    try:
      fcntl.fcntl(file_descriptor, F_NOCACHE, 1)
    except OSError:
      pass

def _write_flags():
  # Prefer O_DSYNC on Linux so each write is durable (a true device write); macOS relies on F_NOCACHE instead
  flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
  if hasattr(os, 'O_DSYNC') and sys.platform != 'darwin':
    flags |= os.O_DSYNC
  return flags

def _evict_read_cache(file_descriptor, offset, length):
  # On Linux, drop the page cache for the region we are about to read so the read hits the device
  if hasattr(os, 'posix_fadvise'):
    try:
      os.posix_fadvise(file_descriptor, offset, length, os.POSIX_FADV_DONTNEED)
    except OSError:
      pass

def _result(total_bytes, operations, elapsed_s, latencies_s):
  # Package one test's raw counters into the metrics rpi-sdinfo reports. MBps is base-10 (matching card branding)
  return {
    'mbps': (total_bytes / 1000000) / elapsed_s if elapsed_s else 0.0,
    'iops': operations / elapsed_s if elapsed_s else 0.0,
    'lat_ms': (statistics.mean(latencies_s) * 1000) if latencies_s else 0.0
  }

#======================================
# The three benchmark primitives
#--------------------------------------

def sequential_write(path, size_bytes, block_size=SEQ_BLOCK):
  # Write size_bytes to path in block_size chunks and time it. Creates/truncates the file to size_bytes
  block_size = min(block_size, size_bytes) or size_bytes
  blocks = max(1, size_bytes // block_size)
  buffer = os.urandom(block_size)  # Random data so a card/controller that dedupes or compresses can't cheat
  latencies = []
  file_descriptor = os.open(path, _write_flags(), 0o644)
  try:
    _disable_cache(file_descriptor)
    start = time.perf_counter()
    for _ in range(blocks):
      operation_start = time.perf_counter()
      os.write(file_descriptor, buffer)
      latencies.append(time.perf_counter() - operation_start)
    os.fsync(file_descriptor)
    elapsed = time.perf_counter() - start
  finally:
    os.close(file_descriptor)
  return _result(blocks * block_size, blocks, elapsed, latencies)

def random_io(path, size_bytes, mode, duration_s=DEFAULT_SECONDS, block_size=RAND_BLOCK):
  # Do random block_size reads or writes at aligned offsets across an existing size_bytes file for duration_s
  aligned_blocks = max(1, (size_bytes - block_size) // block_size)
  buffer = os.urandom(block_size) if mode == 'write' else None
  latencies = []
  operations = 0
  flags = os.O_RDWR | (os.O_DSYNC if (mode == 'write' and hasattr(os, 'O_DSYNC') and sys.platform != 'darwin') else 0)
  file_descriptor = os.open(path, flags)
  try:
    _disable_cache(file_descriptor)
    deadline = time.perf_counter() + duration_s
    start = time.perf_counter()
    while time.perf_counter() < deadline:
      offset = random.randint(0, aligned_blocks) * block_size
      if mode == 'read':
        _evict_read_cache(file_descriptor, offset, block_size)
        operation_start = time.perf_counter()
        os.pread(file_descriptor, block_size, offset)
      else:
        operation_start = time.perf_counter()
        os.pwrite(file_descriptor, buffer, offset)
      latencies.append(time.perf_counter() - operation_start)
      operations += 1
    if mode == 'write':
      os.fsync(file_descriptor)
    elapsed = time.perf_counter() - start
  finally:
    os.close(file_descriptor)
  return _result(operations * block_size, operations, elapsed, latencies)

#======================================
# Orchestration
#--------------------------------------

def benchmark_once(path, size_bytes, duration_s=DEFAULT_SECONDS):
  # Run the full A1-style suite once against the file at path, returning per-test metrics
  return {
    'seq_write': sequential_write(path, size_bytes),
    'rand_write': random_io(path, size_bytes, 'write', duration_s),
    'rand_read': random_io(path, size_bytes, 'read', duration_s)
  }

def empty_results():
  # The list-of-samples structure rpi-sdinfo aggregates over. Keys mirror the old fio result shape
  return {
    'write': {'seq_mbps': [], 'seq_iops': [], 'seq_latency': [],
              'rand_4kb_mbps': [], 'rand_4kb_iops': [], 'rand_4kb_latency': []},
    'read': {'rand_4kb_mbps': [], 'rand_4kb_iops': [], 'rand_4kb_latency': []}
  }

def run(path, runs=DEFAULT_RUNS, size_bytes=DEFAULT_SIZE_MB * 1024 * 1024, duration_s=DEFAULT_SECONDS, on_run=None):
  # Run the suite `runs` times, collecting samples into the rpi-sdinfo result structure.
  # `on_run(run_number, run_metrics)` is an optional callback invoked after each run (e.g. to print progress).
  results = empty_results()
  for run_number in range(1, runs + 1):
    metrics = benchmark_once(path, size_bytes, duration_s)
    results['write']['seq_mbps'].append(metrics['seq_write']['mbps'])
    results['write']['seq_iops'].append(metrics['seq_write']['iops'])
    results['write']['seq_latency'].append(metrics['seq_write']['lat_ms'])
    results['write']['rand_4kb_mbps'].append(metrics['rand_write']['mbps'])
    results['write']['rand_4kb_iops'].append(metrics['rand_write']['iops'])
    results['write']['rand_4kb_latency'].append(metrics['rand_write']['lat_ms'])
    results['read']['rand_4kb_mbps'].append(metrics['rand_read']['mbps'])
    results['read']['rand_4kb_iops'].append(metrics['rand_read']['iops'])
    results['read']['rand_4kb_latency'].append(metrics['rand_read']['lat_ms'])
    if on_run:
      on_run(run_number, metrics)
  return results

#======================================
# Standalone command line entry point
#--------------------------------------

def main(argv=None):
  parser = argparse.ArgumentParser(description='Native, dependency-free SD/MMC storage benchmark (A1 sniff test).')
  parser.add_argument('--dir', default=tempfile.gettempdir(), help='Directory on the card to test (default: system temp dir)')
  parser.add_argument('--runs', type=int, default=DEFAULT_RUNS, help='Number of benchmark runs to average (default: %(default)s)')
  parser.add_argument('--size-mb', type=int, default=DEFAULT_SIZE_MB, help='Test file size in MiB (default: %(default)s)')
  parser.add_argument('--seconds', type=int, default=DEFAULT_SECONDS, help='Duration of each random IO test (default: %(default)s)')
  parser.add_argument('--keep', action='store_true', help='Keep the test file instead of deleting it')
  args = parser.parse_args(argv)

  test_file = os.path.join(args.dir, 'sd.test.file')
  size_bytes = args.size_mb * 1024 * 1024
  print(f'Benchmarking {args.dir} with a {args.size_mb} MiB file, {args.runs} run(s). This is non-destructive.')
  print('                   Sequential write            Random 4 KiB write           Random 4 KiB read')

  def show(run_number, metrics):
    sw, rw, rr = metrics['seq_write'], metrics['rand_write'], metrics['rand_read']
    print(f'   Run {run_number} of {args.runs}: '
          f'{sw["mbps"]:8.1f} MBps {sw["iops"]:7.0f} IOPS   '
          f'{rw["mbps"]:8.1f} MBps {rw["iops"]:7.0f} IOPS   '
          f'{rr["mbps"]:8.1f} MBps {rr["iops"]:7.0f} IOPS')

  try:
    results = run(test_file, args.runs, size_bytes, args.seconds, on_run=show)
  finally:
    if not args.keep and os.path.isfile(test_file):
      os.remove(test_file)

  print('\nMean over all runs:')
  print(f'   Sequential write:  {statistics.mean(results["write"]["seq_mbps"]):.1f} MBps, '
        f'{statistics.mean(results["write"]["seq_iops"]):.0f} IOPS')
  print(f'   Random 4 KiB write:{statistics.mean(results["write"]["rand_4kb_mbps"]):.2f} MBps, '
        f'{statistics.mean(results["write"]["rand_4kb_iops"]):.0f} IOPS')
  print(f'   Random 4 KiB read: {statistics.mean(results["read"]["rand_4kb_mbps"]):.2f} MBps, '
        f'{statistics.mean(results["read"]["rand_4kb_iops"]):.0f} IOPS')
  return 0

if __name__ == '__main__':
  sys.exit(main())
