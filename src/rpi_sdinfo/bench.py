#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.3-20260705
# File:         src/rpi_sdinfo/bench.py
# License:      Apache-2.0
# Language:     Python 3.6 or later
# Source:       https://github.com/mike548141/rpi
#
# Description:
#   A small, dependency-free storage benchmark that replaces the external `fio` tool used by rpi-sdinfo.
#   It emulates the SD Association Application Performance Class 1 (A1) sniff test: sequential write
#   throughput, plus random 4 KiB write and read IOPS. Pure Python standard library only, so it runs on
#   Raspberry Pi Linux, macOS, and Windows (and anywhere else CPython does) with nothing to install.
#
#   This is a sniff test, not a certified benchmark. The card is not put into the fresh, aligned state the
#   SD specification requires, and without kernel O_DIRECT we lean on cache-bypassing hints instead:
#     * macOS   - F_NOCACHE on the file descriptor (fcntl) so IO bypasses the unified buffer cache.
#     * Linux   - O_DSYNC on writes (each write reaches the device) and posix_fadvise(DONTNEED) before reads
#                 so reads miss the page cache. Falls back to a final fsync() where those are unavailable.
#     * Windows - no user-space cache-bypass flag, so writes use O_DSYNC-equivalent fsync durability and the
#                 numbers lean a little optimistic on reads; still enough to spot a slow or fake card.
#   The numbers are good enough to tell a genuine class-10/A1 card from a slow or counterfeit one, which is
#   all rpi-sdinfo needs. For the capacity-fraud (fake-card) sweep see verify.py; ROADMAP.md tracks the path
#   to a true O_DIRECT benchmark.
#
# Usage (standalone):
#   rpi-sdbench [--dir /var/tmp] [--runs 3] [--size-mb 64] [--seconds 10] [--json]
#   The test file is created in --dir (default the system temp dir) and removed afterwards. Point --dir at a
#   path on the card you want to test. --json prints machine-readable results to stdout.

import argparse
import json
import math
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

# Open in binary mode where the OS distinguishes it (Windows), a no-op elsewhere. Without this Windows would
# translate bytes and corrupt the timing/size maths
O_BINARY = getattr(os, 'O_BINARY', 0)

# os.pread / os.pwrite are POSIX-only. On Windows fall back to seek-then-read/write. We are single-threaded so
# the non-atomic seek+IO is safe here
if hasattr(os, 'pread'):
  def _pread(file_descriptor, length, offset):
    return os.pread(file_descriptor, length, offset)
  def _pwrite(file_descriptor, data, offset):
    return os.pwrite(file_descriptor, data, offset)
else:
  def _pread(file_descriptor, length, offset):
    os.lseek(file_descriptor, offset, os.SEEK_SET)
    return os.read(file_descriptor, length)
  def _pwrite(file_descriptor, data, offset):
    os.lseek(file_descriptor, offset, os.SEEK_SET)
    return os.write(file_descriptor, data)

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
  flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
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

def _percentile(sorted_vals, q):
  # Linear-interpolation percentile (q in 0..100) over an already-sorted, non-empty list. Avoids
  # statistics.quantiles so we stay on the 3.6 floor this tool targets
  if not sorted_vals:
    return 0.0
  if len(sorted_vals) == 1:
    return sorted_vals[0]
  rank = (q / 100.0) * (len(sorted_vals) - 1)
  low = int(math.floor(rank))
  high = int(math.ceil(rank))
  if low == high:
    return sorted_vals[low]
  return sorted_vals[low] * (high - rank) + sorted_vals[high] * (rank - low)

def _latency_stats(latencies_s):
  # Reduce every per-operation latency (seconds) to a distribution in milliseconds. A mean alone hides the tail
  # that actually hurts on a worn or fake card, so expose p50/p95/p99 and the extremes too
  if not latencies_s:
    return {'mean_ms': 0.0, 'p50_ms': 0.0, 'p95_ms': 0.0, 'p99_ms': 0.0, 'min_ms': 0.0, 'max_ms': 0.0}
  ms = sorted(value * 1000 for value in latencies_s)
  return {
    'mean_ms': statistics.mean(ms),
    'p50_ms': _percentile(ms, 50),
    'p95_ms': _percentile(ms, 95),
    'p99_ms': _percentile(ms, 99),
    'min_ms': ms[0],
    'max_ms': ms[-1],
  }

def _result(total_bytes, operations, elapsed_s, latencies_s):
  # Package one test's raw counters into the metrics rpi-sdinfo reports. MBps is base-10 (matching card branding).
  # `lat_ms` stays the mean (backward compatible); `lat` carries the full percentile breakdown
  lat = _latency_stats(latencies_s)
  return {
    'mbps': (total_bytes / 1000000) / elapsed_s if elapsed_s else 0.0,
    'iops': operations / elapsed_s if elapsed_s else 0.0,
    'lat_ms': lat['mean_ms'],
    'lat': lat,
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
  flags = os.O_RDWR | O_BINARY | (os.O_DSYNC if (mode == 'write' and hasattr(os, 'O_DSYNC') and sys.platform != 'darwin') else 0)
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
        _pread(file_descriptor, block_size, offset)
      else:
        operation_start = time.perf_counter()
        _pwrite(file_descriptor, buffer, offset)
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

def benchmark_once(path, size_bytes, duration_s=DEFAULT_SECONDS, on_phase=None):
  # Run the full A1-style suite once against the file at path, returning per-test metrics.
  # `on_phase(name)` is an optional callback fired before each phase (e.g. to drive a progress spinner)
  def phase(name):
    if on_phase:
      on_phase(name)
  phase('sequential write')
  seq_write = sequential_write(path, size_bytes)
  phase('random 4 KiB write')
  rand_write = random_io(path, size_bytes, 'write', duration_s)
  phase('random 4 KiB read')
  rand_read = random_io(path, size_bytes, 'read', duration_s)
  return {'seq_write': seq_write, 'rand_write': rand_write, 'rand_read': rand_read}

def empty_results():
  # The list-of-samples structure rpi-sdinfo aggregates over. Keys mirror the old fio result shape.
  # `*_latency` stays the per-run mean (ms) for compatibility; `*_latency_pct` adds the per-run percentile dicts
  return {
    'write': {'seq_mbps': [], 'seq_iops': [], 'seq_latency': [], 'seq_latency_pct': [],
              'rand_4kb_mbps': [], 'rand_4kb_iops': [], 'rand_4kb_latency': [], 'rand_4kb_latency_pct': []},
    'read': {'rand_4kb_mbps': [], 'rand_4kb_iops': [], 'rand_4kb_latency': [], 'rand_4kb_latency_pct': []}
  }

def run(path, runs=DEFAULT_RUNS, size_bytes=DEFAULT_SIZE_MB * 1024 * 1024, duration_s=DEFAULT_SECONDS, on_run=None, on_phase=None):
  # Run the suite `runs` times, collecting samples into the rpi-sdinfo result structure.
  # `on_run(run_number, run_metrics)` fires after each run; `on_phase(run_number, phase_name)` fires before each
  # phase within a run - both optional, both purely for progress reporting.
  results = empty_results()
  for run_number in range(1, runs + 1):
    phase_cb = (lambda name, n=run_number: on_phase(n, name)) if on_phase else None
    metrics = benchmark_once(path, size_bytes, duration_s, on_phase=phase_cb)
    results['write']['seq_mbps'].append(metrics['seq_write']['mbps'])
    results['write']['seq_iops'].append(metrics['seq_write']['iops'])
    results['write']['seq_latency'].append(metrics['seq_write']['lat_ms'])
    results['write']['seq_latency_pct'].append(metrics['seq_write']['lat'])
    results['write']['rand_4kb_mbps'].append(metrics['rand_write']['mbps'])
    results['write']['rand_4kb_iops'].append(metrics['rand_write']['iops'])
    results['write']['rand_4kb_latency'].append(metrics['rand_write']['lat_ms'])
    results['write']['rand_4kb_latency_pct'].append(metrics['rand_write']['lat'])
    results['read']['rand_4kb_mbps'].append(metrics['rand_read']['mbps'])
    results['read']['rand_4kb_iops'].append(metrics['rand_read']['iops'])
    results['read']['rand_4kb_latency'].append(metrics['rand_read']['lat_ms'])
    results['read']['rand_4kb_latency_pct'].append(metrics['rand_read']['lat'])
    if on_run:
      on_run(run_number, metrics)
  return results

#======================================
# Standalone command line entry point
#--------------------------------------

def aggregate_latency(pct_list):
  # Combine the per-run latency dicts (from _latency_stats) into one distribution: mean the central percentiles,
  # but keep the true min and max across every run. Returns zeros when no runs were recorded
  if not pct_list:
    return {'mean_ms': 0.0, 'p50_ms': 0.0, 'p95_ms': 0.0, 'p99_ms': 0.0, 'min_ms': 0.0, 'max_ms': 0.0}
  agg = {key: statistics.mean(d.get(key, 0.0) for d in pct_list) for key in ('mean_ms', 'p50_ms', 'p95_ms', 'p99_ms')}
  agg['min_ms'] = min(d.get('min_ms', 0.0) for d in pct_list)
  agg['max_ms'] = max(d.get('max_ms', 0.0) for d in pct_list)
  return agg

def summary(results):
  # Reduce the per-run sample lists to the mean of each headline metric plus a combined latency distribution
  # (used by both the text and JSON output)
  return {
    'seq_write': {'mbps': statistics.mean(results['write']['seq_mbps']),
                  'iops': statistics.mean(results['write']['seq_iops']),
                  'lat': aggregate_latency(results['write']['seq_latency_pct'])},
    'rand_write': {'mbps': statistics.mean(results['write']['rand_4kb_mbps']),
                   'iops': statistics.mean(results['write']['rand_4kb_iops']),
                   'lat': aggregate_latency(results['write']['rand_4kb_latency_pct'])},
    'rand_read': {'mbps': statistics.mean(results['read']['rand_4kb_mbps']),
                  'iops': statistics.mean(results['read']['rand_4kb_iops']),
                  'lat': aggregate_latency(results['read']['rand_4kb_latency_pct'])},
  }

def main(argv=None):
  parser = argparse.ArgumentParser(description='Native, dependency-free SD/MMC storage benchmark (A1 sniff test).')
  parser.add_argument('--dir', default=tempfile.gettempdir(), help='Directory on the card to test (default: system temp dir)')
  parser.add_argument('--runs', type=int, default=DEFAULT_RUNS, help='Number of benchmark runs to average (default: %(default)s)')
  parser.add_argument('--size-mb', type=int, default=DEFAULT_SIZE_MB, help='Test file size in MiB (default: %(default)s)')
  parser.add_argument('--seconds', type=int, default=DEFAULT_SECONDS, help='Duration of each random IO test (default: %(default)s)')
  parser.add_argument('--keep', action='store_true', help='Keep the test file instead of deleting it')
  parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON to stdout (progress on stderr)')
  args = parser.parse_args(argv)

  # In JSON mode stdout must carry only the JSON document, so all human progress goes to stderr
  from . import ui
  status = ui.Console(sys.stderr if args.json else sys.stdout)
  spinner = ui.Spinner(status)

  test_file = os.path.join(args.dir, 'sd.test.file')
  size_bytes = args.size_mb * 1024 * 1024

  status.section('Benchmark', f'{args.size_mb} MiB file in {args.dir} {status.g["dot"]} {args.runs} run(s) {status.g["dot"]} non-destructive')
  status.kv('Sequential write', '512 KiB blocks')
  status.kv('Random 4 KiB', f'read + write, {args.seconds}s each')
  status.out('')

  def on_phase(run_number, name):
    spinner.update(f'Run {run_number}/{args.runs}  {name}...')

  def on_run(run_number, metrics):
    spinner.clear()
    sw, rw, rr = metrics['seq_write'], metrics['rand_write'], metrics['rand_read']
    status.line(f'Run {run_number}/{args.runs}   '
                f'{status.style("seq", "grey")} {sw["mbps"]:7.1f} MBps   '
                f'{status.style("wr", "grey")} {rw["iops"]:6.0f} IOPS   '
                f'{status.style("rd", "grey")} {rr["iops"]:6.0f} IOPS')

  try:
    results = run(test_file, args.runs, size_bytes, args.seconds, on_run=on_run, on_phase=on_phase)
  finally:
    spinner.stop()
    if not args.keep and os.path.isfile(test_file):
      os.remove(test_file)

  means = summary(results)
  if args.json:
    print(json.dumps({'dir': args.dir, 'runs': args.runs, 'size_mb': args.size_mb,
                      'seconds': args.seconds, 'mean': means, 'samples': results}, indent=2))
    return 0

  status.section('Mean over all runs')
  status.kv('Sequential write', f'{means["seq_write"]["mbps"]:.1f} MBps', value_style='bold', note=f'p95 {means["seq_write"]["lat"]["p95_ms"]:.2f} ms')
  status.kv('Random 4 KiB write', f'{means["rand_write"]["iops"]:.0f} IOPS ({means["rand_write"]["mbps"]:.2f} MBps)', value_style='bold', note=f'p95 {means["rand_write"]["lat"]["p95_ms"]:.2f} ms')
  status.kv('Random 4 KiB read', f'{means["rand_read"]["iops"]:.0f} IOPS ({means["rand_read"]["mbps"]:.2f} MBps)', value_style='bold', note=f'p95 {means["rand_read"]["lat"]["p95_ms"]:.2f} ms')

  status.section('Latency', 'ms per operation')
  for label, key in (('Sequential write', 'seq_write'), ('Random 4 KiB write', 'rand_write'), ('Random 4 KiB read', 'rand_read')):
    lat = means[key]['lat']
    status.kv(label, f'p50 {lat["p50_ms"]:.2f}  {status.g["dot"]}  p95 {lat["p95_ms"]:.2f}  {status.g["dot"]}  p99 {lat["p99_ms"]:.2f}', note=f'max {lat["max_ms"]:.2f}')
  status.out('')
  return 0

if __name__ == '__main__':
  sys.exit(main())
