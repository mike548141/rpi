#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.1-20260705
# File:         sdverify.py
# License:      GNU GPL v3
# Language:     Python 3.6 or later
# Source:       https://github.com/mike548141/rpi
#
# Description:
#   A dependency-free capacity-fraud sweep for SD/MMC cards (and USB sticks), the pure-Python cousin of
#   f3 (f3write/f3read) and h2testw. The classic counterfeit is a small flash chip whose controller lies
#   about its size: a 16 GB chip that reports 512 GB. Writing past the real capacity silently wraps back
#   over earlier data (or is thrown away), so the fraud is invisible until you actually fill the card and
#   read it back. This tool does exactly that.
#
#   How it works, and why it is trustworthy:
#     * We fill the card's free space with test files, each block stamped with a pattern derived from its
#       absolute offset in the sweep (SHAKE-128 keyed by offset). Every offset therefore holds unique,
#       non-compressible data that cannot be guessed, stored cheaply, or deduplicated by a cheating
#       controller.
#     * We then read every block back and regenerate the expected pattern from its offset. A genuine card
#       returns exactly what was written. A fake returns zeros, garbage, or an *earlier* block's pattern
#       (address wrap) - all of which fail the comparison. The offset of the first failure is the card's
#       true usable capacity.
#     * Reads bypass the OS cache (F_NOCACHE on macOS, posix_fadvise(DONTNEED) on Linux) so we measure the
#       device, not RAM - otherwise a fake would "pass" by serving the data we just wrote from the page
#       cache. The IO helpers are shared with sdbench.py.
#
#   This is non-destructive to existing files (it only adds its own, then deletes them) but it does fill
#   the card's free space and writes its full capacity once, so it takes time and adds a little flash wear.
#   It is strictly opt-in. A safety margin of free space is always left so the filesystem is never wedged.
#
# Usage (standalone):
#   python3 sdverify.py --dir /Volumes/CARD [--file-size-mb 1024] [--block-kb 4096]
#                       [--capacity-mb N] [--keep] [--json]
#   --dir must point at a mounted, writable path on the card under test. Without --capacity-mb the whole
#   free space is swept. Test files are removed afterwards unless --keep is given.
#
# Exit codes: 0 genuine (all written data verified) · 1 fraud/corruption detected · 2 usage/IO error

import argparse
import errno
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

# Cache-bypassing IO primitives are shared with the benchmark so the two tools never diverge on how they
# reach the device rather than RAM (_disable_cache, _evict_read_cache, portable _pread/_pwrite, O_BINARY)
import sdbench

#======================================
# Constants
#--------------------------------------

# Prefix for the temporary test files we create in the target directory
FILE_PREFIX = 'rpi-sdverify.'
FILE_SUFFIX = '.dat'

# A fixed key mixed into every pattern. It only has to be constant across the write and verify phases so the
# expected bytes can be regenerated; it is not a secret and carries no anonymity role
PATTERN_KEY = b'rpi-sdverify/1'

DEFAULT_FILE_MB = 1024      # Size of each test file (many small files rather than one huge one)
DEFAULT_BLOCK_KB = 4096     # IO + pattern granularity: 4 MiB balances hashing cost against syscall overhead

# Never fill the filesystem to the brim - leave the larger of this many bytes or a small fraction free so the
# card (and the OS, if this is the boot volume) is not wedged by a full disk
SAFETY_MARGIN_BYTES = 64 * 1024 * 1024
SAFETY_MARGIN_FRACTION = 0.01

#======================================
# The offset-keyed pattern
#--------------------------------------

def pattern_block(offset, length):
  # Deterministic, non-compressible bytes unique to this absolute offset in the sweep. SHAKE-128 is an
  # extendable-output hash, so one call yields exactly `length` bytes seeded by the offset. Regenerating the
  # same offset during verification reproduces the bytes bit-for-bit without us storing the payload
  seed = PATTERN_KEY + offset.to_bytes(8, 'big')
  return hashlib.shake_128(seed).digest(length)

#======================================
# Sizing
#--------------------------------------

def plan_sweep(path, capacity_bytes=None, margin_bytes=SAFETY_MARGIN_BYTES, margin_fraction=SAFETY_MARGIN_FRACTION):
  # Decide how many bytes to write: the free space on `path`'s filesystem less a safety margin, optionally
  # capped by capacity_bytes. Returns (sweep_bytes, usage) where usage is the shutil.disk_usage snapshot
  usage = shutil.disk_usage(path)
  margin = max(margin_bytes, int(usage.total * margin_fraction))
  sweep = max(0, usage.free - margin)
  if capacity_bytes is not None:
    sweep = min(sweep, capacity_bytes)
  return sweep, usage

#======================================
# Write phase
#--------------------------------------

def _open_write(path):
  file_descriptor = os.open(path, sdbench._write_flags(), 0o644)
  sdbench._disable_cache(file_descriptor)
  return file_descriptor

def write_sweep(directory, sweep_bytes, file_bytes, block_bytes, on_progress=None):
  # Fill `directory` with test files totalling up to sweep_bytes, each block stamped with its absolute-offset
  # pattern. Returns (files, written_bytes, short) where files is a list of (path, start_offset, length) and
  # `short` is True if we stopped early on a full filesystem (ENOSPC) before reaching sweep_bytes
  files = []
  written = 0
  short = False
  index = 0
  while written < sweep_bytes and not short:
    this_file = min(file_bytes, sweep_bytes - written)
    path = os.path.join(directory, FILE_PREFIX + ('%05d' % index) + FILE_SUFFIX)
    start = written
    file_written = 0
    file_descriptor = _open_write(path)
    try:
      while file_written < this_file:
        chunk = min(block_bytes, this_file - file_written)
        data = pattern_block(start + file_written, chunk)
        try:
          view = memoryview(data)
          while view:
            view = view[os.write(file_descriptor, view):]
        except OSError as error:
          if error.errno == errno.ENOSPC:
            short = True
            break
          raise
        file_written += chunk
        written += chunk
        if on_progress:
          on_progress('write', written, sweep_bytes)
      os.fsync(file_descriptor)
    finally:
      os.close(file_descriptor)
    if file_written:
      files.append((path, start, file_written))
    index += 1
  return files, written, short

#======================================
# Verify phase
#--------------------------------------

def _open_read(path):
  file_descriptor = os.open(path, os.O_RDONLY | sdbench.O_BINARY)
  sdbench._disable_cache(file_descriptor)
  return file_descriptor

def verify_sweep(files, block_bytes, on_progress=None, total_bytes=None):
  # Read every file back and compare each block against the pattern regenerated from its absolute offset.
  # Returns (good_bytes, first_bad_offset): good_bytes is the contiguous run that verified from offset 0, and
  # first_bad_offset is where the first mismatch was found (None if everything verified)
  good = 0
  for path, start, length in files:
    file_descriptor = _open_read(path)
    try:
      position = 0
      while position < length:
        chunk = min(block_bytes, length - position)
        offset = start + position
        sdbench._evict_read_cache(file_descriptor, offset - start, chunk)
        data = sdbench._pread(file_descriptor, chunk, position)
        if data != pattern_block(offset, chunk):
          # Compare byte-for-byte to find exactly where the good data ends inside this block
          expected = pattern_block(offset, chunk)
          matched = 0
          for a, b in zip(data, expected):
            if a != b:
              break
            matched += 1
          return good + matched, offset + matched
        good += chunk
        position += chunk
        if on_progress:
          on_progress('verify', good, total_bytes)
    finally:
      os.close(file_descriptor)
  return good, None

#======================================
# Cleanup
#--------------------------------------

def cleanup(files):
  removed = 0
  for path, _start, _length in files:
    try:
      os.remove(path)
      removed += 1
    except OSError:
      pass
  return removed

#======================================
# Orchestration
#--------------------------------------

def run(directory, capacity_bytes=None, file_bytes=DEFAULT_FILE_MB * 1024 * 1024,
        block_bytes=DEFAULT_BLOCK_KB * 1024, keep=False, on_progress=None, on_phase=None):
  # Full sweep: plan, write, verify, clean up. Returns a result dict describing what was tested and the
  # verdict. `on_phase(name)` fires at the start of each phase; `on_progress(phase, done, total)` streams
  # byte counts for a progress display. Never raises on a mismatch - that is reported in the result
  if on_phase:
    on_phase('plan')
  sweep_bytes, usage = plan_sweep(directory, capacity_bytes)
  result = {
    'dir': directory,
    'block_bytes': block_bytes,
    'file_bytes': file_bytes,
    'reported_free_bytes': usage.free,
    'reported_total_bytes': usage.total,
    'used_before_bytes': usage.used,
    'swept_bytes': 0,
    'verified_bytes': 0,
    'first_bad_offset': None,
    'short': False,
    'usable_estimate_bytes': None,
    'ok': False,
    'reason': '',
  }
  if sweep_bytes <= 0:
    result['reason'] = 'no free space to test (need more than the safety margin free)'
    return result

  files = []
  try:
    if on_phase:
      on_phase('write')
    files, written, short = write_sweep(directory, sweep_bytes, file_bytes, block_bytes, on_progress)
    result['swept_bytes'] = written
    result['short'] = short

    if on_phase:
      on_phase('verify')
    verified, first_bad = verify_sweep(files, block_bytes, on_progress, total_bytes=written)
    result['verified_bytes'] = verified
    result['first_bad_offset'] = first_bad
  finally:
    if not keep and files:
      if on_phase:
        on_phase('cleanup')
      cleanup(files)

  # A genuine card verifies every byte it accepted. The usable capacity is what was already in use plus the
  # span that read back correctly; on a fake that is far short of the reported total
  result['usable_estimate_bytes'] = usage.used + result['verified_bytes']
  if result['first_bad_offset'] is None:
    result['ok'] = True
    result['reason'] = ('all %d bytes written verified' % result['verified_bytes']) + (
      ' (free space not fully swept - capped)' if capacity_bytes is not None else '')
  else:
    result['ok'] = False
    result['reason'] = 'data mismatch at offset %d - card is smaller than it reports (counterfeit) or failing' % result['first_bad_offset']
  return result

#======================================
# Standalone CLI
#--------------------------------------

def _human(num_bytes):
  # Base-10 sizes, matching how cards are branded and how sdbench reports throughput
  value = float(num_bytes)
  for unit in ('B', 'kB', 'MB', 'GB', 'TB'):
    if abs(value) < 1000 or unit == 'TB':
      return ('%.0f %s' % (value, unit)) if unit == 'B' else ('%.2f %s' % (value, unit))
    value /= 1000
  return '%.2f TB' % value

def main(argv=None):
  parser = argparse.ArgumentParser(description='Native, dependency-free SD/MMC capacity-fraud sweep (f3/h2testw style).')
  parser.add_argument('--dir', default=tempfile.gettempdir(), help='Directory on the card to sweep (default: system temp dir). Point this at the mounted card.')
  parser.add_argument('--file-size-mb', type=int, default=DEFAULT_FILE_MB, help='Size of each test file in MiB (default: %(default)s)')
  parser.add_argument('--block-kb', type=int, default=DEFAULT_BLOCK_KB, help='IO/pattern block size in KiB (default: %(default)s)')
  parser.add_argument('--capacity-mb', type=int, default=None, help='Cap the sweep to this many MiB instead of filling all free space')
  parser.add_argument('--keep', action='store_true', help='Keep the test files instead of deleting them')
  parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON to stdout (progress on stderr)')
  args = parser.parse_args(argv)

  if not os.path.isdir(args.dir):
    sys.stderr.write('sdverify: --dir is not a directory: ' + args.dir + '\n')
    return 2

  cap = args.capacity_mb * 1024 * 1024 if args.capacity_mb is not None else None
  quiet = args.json

  def on_phase(name):
    if not quiet:
      sys.stderr.write('\n' + {'plan': 'Planning sweep…', 'write': 'Writing test data…',
                               'verify': 'Verifying…', 'cleanup': 'Cleaning up…'}.get(name, name) + '\n')

  last = [0.0]
  def on_progress(phase, done, total):
    if quiet or total is None:
      return
    now = time.perf_counter()
    if now - last[0] < 0.2 and done < total:
      return
    last[0] = now
    pct = (100.0 * done / total) if total else 0.0
    sys.stderr.write('\r  %-7s %5.1f%%  %s / %s   ' % (phase, pct, _human(done), _human(total)))
    sys.stderr.flush()

  try:
    result = run(args.dir, cap, args.file_size_mb * 1024 * 1024, args.block_kb * 1024,
                 keep=args.keep, on_progress=on_progress, on_phase=on_phase)
  except OSError as error:
    sys.stderr.write('\nsdverify: IO error: ' + str(error) + '\n')
    return 2

  if not quiet:
    sys.stderr.write('\n')

  if args.json:
    print(json.dumps(result, indent=2))
  else:
    print('')
    print('CAPACITY SWEEP  ' + result['dir'])
    print('  Reported capacity:  ' + _human(result['reported_total_bytes']))
    print('  Swept (free space): ' + _human(result['swept_bytes']) + ('  (stopped early: filesystem full)' if result['short'] else ''))
    print('  Verified good:      ' + _human(result['verified_bytes']))
    print('  Usable estimate:    ' + _human(result['usable_estimate_bytes']))
    if result['first_bad_offset'] is not None:
      print('  First bad offset:   ' + _human(result['first_bad_offset']))
    print('')
    print(('  GENUINE - ' if result['ok'] else '  SUSPECT - ') + result['reason'])

  return 0 if result['ok'] else 1

if __name__ == '__main__':
  sys.exit(main())
