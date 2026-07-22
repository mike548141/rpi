#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.2-20260705
# File:         src/rpi_sdinfo/verify.py
# License:      Apache-2.0
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
#       cache. The IO helpers are shared with bench.py.
#
#   This is non-destructive to existing files (it only adds its own, then deletes them) but it does fill
#   the card's free space and writes its full capacity once, so it takes time and adds a little flash wear.
#   It is strictly opt-in. A safety margin of free space is always left so the filesystem is never wedged.
#
# There is also a fast, DESTRUCTIVE alternative: a raw-device "corners" sweep (--device). Instead of filling
# the card it probes only block 0, every power-of-two offset, and the last block of the *reported* capacity.
# A counterfeit truncates the block address at a power-of-two boundary R, so logical block 0 and logical block
# R alias onto the same physical cell; because R is itself one of the probed offsets, the pair (0, R) is always
# tested - guaranteeing the fake is caught in ~log2(N) probes (29 for a 512 GB card) rather than a full write.
# It cannot be done at the filesystem level (the allocator would hide the aliasing), so it writes the raw
# device directly and is gated behind --yes plus a mounted-device refusal. It reliably catches the standard
# power-of-two fake; an odd non-power-of-two wrap can still need the exhaustive sweep below.
#
# The exhaustive raw-device backstop is the DESTRUCTIVE "full" sweep (--device --full): it writes the
# offset-keyed pattern to EVERY block of the reported capacity, then reads every block back. Unlike the
# free-space sweep it needs no free space (a nearly-full card is tested by overwriting it), and unlike the
# corners sweep it makes no assumption about where the wrap lands - so it catches an *arbitrary* wrap (neither
# a power of two nor a round decimal size) that both the corner and decimal probes can miss. The price is a
# full-capacity write plus a full-capacity read - hours on a big card - which is why corners stays the fast
# default and full is opt-in. It is the raw-device equivalent, in spirit, of an f3/h2testw full fill.
#
# Usage (standalone):
#   rpi-sdverify --dir /Volumes/CARD [--file-size-mb 1024] [--block-kb 4096] [--capacity-mb N] [--keep] [--json]
#     Non-destructive free-space fill sweep. --dir must be a mounted, writable path on the card under test.
#     Without --capacity-mb the whole free space is swept; test files are removed unless --keep is given.
#   rpi-sdverify --device /dev/disk4 --yes [--capacity-mb N] [--block-kb 4096] [--json]
#     DESTRUCTIVE quick corners sweep of a raw block device. Overwrites the device; refuses a mounted one.
#   rpi-sdverify --device /dev/disk4 --full --yes [--capacity-mb N] [--block-kb 4096] [--json]
#     DESTRUCTIVE exhaustive full-capacity sweep of a raw block device: writes and verifies every block.
#     Slow (hours on a big card) but catches arbitrary wraps corners can miss. Refuses a mounted device.
#
# Exit codes: 0 genuine (all written data verified) · 1 fraud/corruption detected · 2 usage/IO error

import argparse
import errno
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

# Cache-bypassing IO primitives are shared with the benchmark so the two tools never diverge on how they
# reach the device rather than RAM (_disable_cache, _evict_read_cache, portable _pread/_pwrite, O_BINARY)
from . import bench as sdbench

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

# Common counterfeit real-capacity boundaries, in bytes. A fake whose real flash is one of these DECIMAL sizes
# wraps its block address at a boundary that is not a power of two, so the power-of-two probe offsets can miss
# it: no probed pair happens to be congruent modulo the wrap (see corner_offsets). Probing each boundary C
# itself busts that congruence - on a card that wraps at C, byte offset C aliases onto physical 0 (C mod C ==
# 0), overwriting block 0, so the read-back of block 0 mismatches. These are the sizes SD cards are actually
# sold as; a fake's real chip (and its wrap) is almost always one of them. Every n*10^9 is a multiple of 512,
# so probing the exact boundary stays block-aligned for raw-device I/O. Binary/GiB reals need no entry here -
# they are already powers of two and thus already in the power-of-two offset set.
COMMON_FAKE_CAPACITIES_BYTES = tuple(
    g * 1000 * 1000 * 1000 for g in
    (1, 2, 4, 8, 16, 30, 32, 50, 60, 64, 100, 120, 128, 200, 240, 250, 256, 400, 500, 512, 1000, 2000))

# Never fill the filesystem to the brim - leave the larger of this many bytes or a small fraction free so the
# card (and the OS, if this is the boot volume) is not wedged by a full disk
SAFETY_MARGIN_BYTES = 64 * 1024 * 1024
SAFETY_MARGIN_FRACTION = 0.01

#======================================
# The offset-keyed pattern
#--------------------------------------

def pattern_block(offset, length):
  """Deterministic, non-compressible bytes unique to this absolute offset in the sweep. SHAKE-128 is an
  extendable-output hash, so one call yields exactly `length` bytes seeded by the offset. Regenerating the
  same offset during verification reproduces the bytes bit-for-bit without us storing the payload
  """
  seed = PATTERN_KEY + offset.to_bytes(8, 'big')
  return hashlib.shake_128(seed).digest(length)

#======================================
# Sizing
#--------------------------------------

def plan_sweep(path, capacity_bytes=None, margin_bytes=SAFETY_MARGIN_BYTES, margin_fraction=SAFETY_MARGIN_FRACTION):
  """Decide how many bytes to write: the free space on `path`'s filesystem less a safety margin, optionally
  capped by capacity_bytes. Returns (sweep_bytes, usage) where usage is the shutil.disk_usage snapshot
  """
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
  """Fill `directory` with test files totalling up to sweep_bytes, each block stamped with its absolute-offset
  pattern. Returns (files, written_bytes, short) where files is a list of (path, start_offset, length) and
  `short` is True if we stopped early on a full filesystem (ENOSPC) before reaching sweep_bytes
  """
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
  """Read every file back and compare each block against the pattern regenerated from its absolute offset.
  Returns (good_bytes, first_bad_offset): good_bytes is the contiguous run that verified from offset 0, and
  first_bad_offset is where the first mismatch was found (None if everything verified)
  """
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
# Raw-device corners sweep (quick fake sniff)
#--------------------------------------
#
# Filling free space (above) is the thorough test, but slow. The quick alternative is to probe only a handful
# of points spread across the *reported* capacity. This only works against the raw device, not the filesystem:
# a fake truncates or wraps the block address, so two probe offsets that are far apart in the reported address
# space collide onto the same physical cell. Writing every probe first, then reading them all back, catches
# that collision - the earlier probe reads back the later probe's pattern. Done at the filesystem level the
# allocator would quietly place every probe inside the small real region and the fake would pass, so this path
# demands a real device (or, for testing, an injected wrapping backend). It is DESTRUCTIVE: it writes directly
# to the device, over any filesystem there.

def corner_offsets(capacity_bytes, block_bytes):
  """Probe block 0, every power-of-two block offset, and the final block. This is not arbitrary: a counterfeit
  truncates the block address at a power-of-two boundary R blocks, so logical block 0 and logical block R
  alias onto the same physical cell. Because R itself is one of the power-of-two offsets we probe, the pair
  (0, R) is always in the set - guaranteeing a detectable collision for any such wrap, with only ~log2(N)
  probes instead of writing the whole card. Evenly-spaced probes would miss it unless two happened to be
  congruent mod R, which is exactly the luck we must not depend on.

  A non-power-of-two wrap (e.g. a real chip of exactly 100 GB) has no power-of-two structure, so none of the
  offsets above need land congruent mod R. To bust that we also probe each common DECIMAL capacity boundary
  below the reported size: if the card really wraps at one of them, that boundary aliases onto block 0 and is
  caught (see COMMON_FAKE_CAPACITIES_BYTES). A truly arbitrary wrap can still slip past both - the thorough
  free-space sweep remains the exhaustive backstop; this stays a fast first pass.
  """
  if capacity_bytes < block_bytes:
    return [0]
  last = ((capacity_bytes - block_bytes) // block_bytes) * block_bytes
  offsets = {0, last}
  step = block_bytes
  while step <= last:
    offsets.add(step)
    step *= 2
  for boundary in COMMON_FAKE_CAPACITIES_BYTES:
    if block_bytes <= boundary <= last:
      offsets.add(boundary)
  return sorted(offsets)

def write_offsets(pwrite, offsets, block_bytes, capacity_bytes, on_progress=None):
  """Write each offset's pattern via the injected pwrite(offset, data). All probes are written before any are
  verified so an address collision on a fake overwrites an earlier probe rather than being hidden
  """
  for index, offset in enumerate(offsets):
    length = min(block_bytes, capacity_bytes - offset)
    pwrite(offset, pattern_block(offset, length))
    if on_progress:
      on_progress('write', index + 1, len(offsets))

def verify_offsets(pread, offsets, block_bytes, capacity_bytes, on_progress=None):
  """Read each probe back via the injected pread(offset, length) and compare to its regenerated pattern.
  Returns (good_count, first_bad_offset) - first_bad_offset is None when every probe verified
  """
  good = 0
  for index, offset in enumerate(offsets):
    length = min(block_bytes, capacity_bytes - offset)
    if pread(offset, length) != pattern_block(offset, length):
      return good, offset
    good += 1
    if on_progress:
      on_progress('verify', index + 1, len(offsets))
  return good, None

def _device_size(path, file_descriptor):
  """Size in bytes of a block device or regular file: seek to the end (works for both), falling back to stat"""
  try:
    size = os.lseek(file_descriptor, 0, os.SEEK_END)
    if size > 0:
      return size
  except OSError:
    pass
  return os.stat(path).st_size

def _device_io(file_descriptor):
  """Build the (pwrite, pread) pair that both raw-device sweeps inject into the shared write/verify helpers.
  pwrite loops until the whole buffer lands (a short pwrite is legal); pread evicts the cache for that span
  first so a fake cannot pass by serving back the bytes we just wrote from the page cache
  """
  def pwrite(offset, data):
    view = memoryview(data)
    while view:
      view = view[os.pwrite(file_descriptor, view, offset + (len(data) - len(view))):]

  def pread(offset, length):
    sdbench._evict_read_cache(file_descriptor, offset, length)
    return sdbench._pread(file_descriptor, length, offset)

  return pwrite, pread

def run_device(device_path, capacity_bytes=None, block_bytes=DEFAULT_BLOCK_KB * 1024,
               on_progress=None, on_phase=None):
  """Quick corners sweep against a raw device (or a regular file, for testing). DESTRUCTIVE on a real device.
  capacity_bytes overrides the detected size (e.g. to probe the branded capacity of a device the OS sizes
  honestly). Returns the same result shape as run(), with 'corners' listing the probed offsets
  """
  if on_phase:
    on_phase('open')
  flags = os.O_RDWR | sdbench.O_BINARY
  if hasattr(os, 'O_DSYNC') and sys.platform != 'darwin':
    flags |= os.O_DSYNC
  file_descriptor = os.open(device_path, flags)
  result = {
    'dir': device_path, 'mode': 'device-corners', 'block_bytes': block_bytes,
    'reported_total_bytes': 0, 'swept_bytes': 0, 'verified_bytes': 0,
    'first_bad_offset': None, 'short': False, 'usable_estimate_bytes': None,
    'corners': [], 'ok': False, 'reason': '',
  }
  try:
    sdbench._disable_cache(file_descriptor)
    total = capacity_bytes or _device_size(device_path, file_descriptor)
    result['reported_total_bytes'] = total
    offsets = corner_offsets(total, block_bytes)
    result['corners'] = offsets

    pwrite, pread = _device_io(file_descriptor)

    if on_phase:
      on_phase('write')
    write_offsets(pwrite, offsets, block_bytes, total, on_progress)
    os.fsync(file_descriptor)

    if on_phase:
      on_phase('verify')
    good, first_bad = verify_offsets(pread, offsets, block_bytes, total, on_progress)
    result['swept_bytes'] = len(offsets) * block_bytes
    result['verified_bytes'] = good * block_bytes
    result['first_bad_offset'] = first_bad
  finally:
    os.fsync(file_descriptor)
    os.close(file_descriptor)

  if result['first_bad_offset'] is None:
    result['ok'] = True
    result['usable_estimate_bytes'] = result['reported_total_bytes']
    result['reason'] = 'all %d probes across the reported capacity verified' % len(result['corners'])
  else:
    result['ok'] = False
    result['usable_estimate_bytes'] = result['first_bad_offset']
    result['reason'] = 'probe at offset %d read back wrong - address wraps below the reported capacity (counterfeit)' % result['first_bad_offset']
  return result

#======================================
# Raw-device FULL sweep (exhaustive backstop)
#--------------------------------------
#
# The corners sweep is fast but assumes the wrap sits on a power-of-two or a common decimal boundary. The full
# sweep makes no such assumption: it writes every block of the reported capacity, then reads every block back,
# so a wrap anywhere is caught. Like corners it needs the raw device (a filesystem allocator would hide the
# aliasing) and is DESTRUCTIVE. Two properties matter for a big card: it holds no payload in RAM (the expected
# bytes are recomputed from the offset via pattern_block, so memory stays O(one block) whatever the capacity),
# and it streams block by block so progress can be reported over a multi-hour run.

def write_full(pwrite, block_bytes, capacity_bytes, on_progress=None):
  """Write the offset-keyed pattern to EVERY block of capacity_bytes via the injected pwrite(offset, data).
  The whole device is written before any of it is verified (see verify_full and run_device_full): a wrap fake
  maps a high block onto an already-written low physical cell, so the corruption only exists once every write
  is laid down - a per-block write-then-read would re-read the just-written block from its aliased cell and
  wrongly pass. Streams block by block; each block's bytes come from pattern_block(offset), never stored
  """
  offset = 0
  while offset < capacity_bytes:
    length = min(block_bytes, capacity_bytes - offset)
    pwrite(offset, pattern_block(offset, length))
    offset += length
    if on_progress:
      on_progress('write', offset, capacity_bytes)

def verify_full(pread, block_bytes, capacity_bytes, on_progress=None):
  """Read every block back via the injected pread(offset, length) and compare to the pattern regenerated from
  its absolute offset. Returns (good_bytes, first_bad_offset): good_bytes is the contiguous run that verified
  from offset 0, first_bad_offset is the byte offset of the first mismatch (None if everything verified). The
  expected bytes are recomputed from the offset, so no copy of the device is ever held in memory
  """
  good = 0
  offset = 0
  while offset < capacity_bytes:
    length = min(block_bytes, capacity_bytes - offset)
    data = pread(offset, length)
    expected = pattern_block(offset, length)
    if data != expected:
      # Compare byte-for-byte to find exactly where the good data ends inside this block
      matched = 0
      for a, b in zip(data, expected):
        if a != b:
          break
        matched += 1
      return good + matched, offset + matched
    good += length
    offset += length
    if on_progress:
      on_progress('verify', offset, capacity_bytes)
  return good, None

def run_device_full(device_path, capacity_bytes=None, block_bytes=DEFAULT_BLOCK_KB * 1024,
                    on_progress=None, on_phase=None):
  """Exhaustive DESTRUCTIVE sweep against a raw device (or a regular file, for testing): write the offset-keyed
  pattern to every block of the reported capacity, then read every block back. Needs no free space and catches
  an arbitrary wrap the corners/decimal probes can miss, at the cost of a full write + full read (hours on a
  big card). capacity_bytes overrides the detected size. Returns the run()/run_device() result shape with mode
  'device-full'; never raises on a mismatch - that is reported in the result
  """
  if on_phase:
    on_phase('open')
  flags = os.O_RDWR | sdbench.O_BINARY
  if hasattr(os, 'O_DSYNC') and sys.platform != 'darwin':
    flags |= os.O_DSYNC
  file_descriptor = os.open(device_path, flags)
  result = {
    'dir': device_path, 'mode': 'device-full', 'block_bytes': block_bytes,
    'reported_total_bytes': 0, 'swept_bytes': 0, 'verified_bytes': 0,
    'first_bad_offset': None, 'short': False, 'usable_estimate_bytes': None,
    'ok': False, 'reason': '',
  }
  try:
    sdbench._disable_cache(file_descriptor)
    total = capacity_bytes or _device_size(device_path, file_descriptor)
    result['reported_total_bytes'] = total
    pwrite, pread = _device_io(file_descriptor)

    if on_phase:
      on_phase('write')
    write_full(pwrite, block_bytes, total, on_progress)
    os.fsync(file_descriptor)

    if on_phase:
      on_phase('verify')
    good, first_bad = verify_full(pread, block_bytes, total, on_progress)
    result['swept_bytes'] = total
    result['verified_bytes'] = good
    result['first_bad_offset'] = first_bad
  finally:
    os.fsync(file_descriptor)
    os.close(file_descriptor)

  if result['first_bad_offset'] is None:
    result['ok'] = True
    result['usable_estimate_bytes'] = result['reported_total_bytes']
    result['reason'] = 'every block across the full reported capacity was written and verified'
  else:
    result['ok'] = False
    result['usable_estimate_bytes'] = result['first_bad_offset']
    result['reason'] = 'block at offset %d read back wrong - address wraps below the reported capacity (counterfeit)' % result['first_bad_offset']
  return result

#======================================
# Cleanup
#--------------------------------------

def cleanup(files):
  """Delete the sweep's test files, ignoring any that are already gone. Returns the count removed."""
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
  """Full sweep: plan, write, verify, clean up. Returns a result dict describing what was tested and the
  verdict. `on_phase(name)` fires at the start of each phase; `on_progress(phase, done, total)` streams
  byte counts for a progress display. Never raises on a mismatch - that is reported in the result
  """
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
  """Base-10 sizes, matching how cards are branded and how sdbench reports throughput"""
  value = float(num_bytes)
  for unit in ('B', 'kB', 'MB', 'GB', 'TB'):
    if abs(value) < 1000 or unit == 'TB':
      return ('%.0f %s' % (value, unit)) if unit == 'B' else ('%.2f %s' % (value, unit))
    value /= 1000
  return '%.2f TB' % value

def looks_mounted(device_path):
  """Best-effort guard: is this block device currently mounted? We refuse to raw-write a mounted device so a
  slip of the finger cannot wipe a live filesystem (or the boot disk). Not exhaustive - the real safety is
  requiring an explicit --device and --yes - but it catches the common mistake
  """
  real = os.path.realpath(device_path)
  candidates = {device_path, real}
  try:
    if sys.platform.startswith('linux'):
      with open('/proc/mounts') as handle:
        for row in handle:
          source = row.split(' ', 1)[0]
          if source in candidates or (real and source.startswith(real)):
            return True
    else:
      # macOS/BSD: parse `mount` output (e.g. "/dev/disk4s1 on /Volumes/CARD (...)")
      output = subprocess.run(['mount'], capture_output=True, text=True).stdout
      for row in output.splitlines():
        source = row.split(' ', 1)[0]
        if source in candidates or (real and source.startswith(real)):
          return True
  except (OSError, ValueError):
    return False
  return False

def _device_progress(quiet):
  last = [0.0]
  def on_progress(phase, done, total):
    if quiet or not total:
      return
    now = time.perf_counter()
    if now - last[0] < 0.1 and done < total:
      return
    last[0] = now
    sys.stderr.write('\r  %-7s probe %d / %d   ' % (phase, done, total))
    sys.stderr.flush()
  return on_progress

def _device_bytes_progress(quiet):
  """Progress line for the full raw sweep, which streams bytes (not a fixed probe count): percent plus human
  bytes done / total, so a multi-hour write or read pass visibly shows it is alive
  """
  last = [0.0]
  def on_progress(phase, done, total):
    if quiet or not total:
      return
    now = time.perf_counter()
    if now - last[0] < 0.2 and done < total:
      return
    last[0] = now
    pct = (100.0 * done / total) if total else 0.0
    sys.stderr.write('\r  %-7s %5.1f%%  %s / %s   ' % (phase, pct, _human(done), _human(total)))
    sys.stderr.flush()
  return on_progress

def _run_device_cli(args, quiet):
  """DESTRUCTIVE raw-device sweep against a raw device (or a plain file, for testing): the fast corner-probe by
  default, or the exhaustive full-capacity write+verify with --full. Both share the same safety gates
  """
  is_block = False
  try:
    is_block = os.path.isfile(args.device) is False and os.stat(args.device).st_mode & 0o170000 == 0o060000
  except OSError as error:
    sys.stderr.write('sdverify: cannot stat --device ' + args.device + ': ' + str(error) + '\n')
    return 2
  if is_block and looks_mounted(args.device):
    sys.stderr.write('sdverify: refusing to write to ' + args.device + ' - it is mounted. Unmount it first.\n')
    return 2
  if not args.yes:
    sys.stderr.write('sdverify: --device does a DESTRUCTIVE raw write to ' + args.device
                     + ', overwriting any data/filesystem on it. Re-run with --yes to confirm.\n')
    return 2

  cap = args.capacity_mb * 1024 * 1024 if args.capacity_mb is not None else None

  if args.full:
    def on_phase(name):
      if not quiet:
        sys.stderr.write('\n' + {'open': 'Opening device…', 'write': 'Writing every block…',
                                 'verify': 'Reading every block back…'}.get(name, name) + '\n')
    try:
      result = run_device_full(args.device, cap, args.block_kb * 1024,
                               on_progress=_device_bytes_progress(quiet), on_phase=on_phase)
    except OSError as error:
      sys.stderr.write('\nsdverify: IO error on ' + args.device + ': ' + str(error) + '\n')
      return 2
  else:
    def on_phase(name):
      if not quiet:
        sys.stderr.write('\n' + {'open': 'Opening device…', 'write': 'Writing corner probes…',
                                 'verify': 'Reading probes back…'}.get(name, name) + '\n')
    try:
      result = run_device(args.device, cap, args.block_kb * 1024,
                          on_progress=_device_progress(quiet), on_phase=on_phase)
    except OSError as error:
      sys.stderr.write('\nsdverify: IO error on ' + args.device + ': ' + str(error) + '\n')
      return 2
  if not quiet:
    sys.stderr.write('\n')

  if args.json:
    print(json.dumps(result, indent=2))
  elif result['mode'] == 'device-full':
    print('')
    print('FULL SWEEP  ' + result['dir'] + '  (every block of the reported capacity written and verified)')
    print('  Reported capacity:  ' + _human(result['reported_total_bytes']))
    print('  Written + verified: ' + _human(result['verified_bytes']))
    if result['first_bad_offset'] is not None:
      print('  First bad offset:   ' + _human(result['first_bad_offset']))
      print('  Usable estimate:    ' + _human(result['usable_estimate_bytes']))
    print('')
    print(('  GENUINE - ' if result['ok'] else '  FAKE - ') + result['reason'])
  else:
    print('')
    print('CORNERS SWEEP  ' + result['dir'] + '  (' + str(len(result['corners'])) + ' probes across the reported capacity)')
    print('  Reported capacity:  ' + _human(result['reported_total_bytes']))
    print('  Written + verified: ' + _human(result['verified_bytes']))
    if result['first_bad_offset'] is not None:
      print('  First bad offset:   ' + _human(result['first_bad_offset']))
      print('  Usable estimate:    ' + _human(result['usable_estimate_bytes']))
    print('')
    print(('  GENUINE - ' if result['ok'] else '  FAKE - ') + result['reason'])
  return 0 if result['ok'] else 1

def main(argv=None):
  """rpi-sdverify entry point: run the free-space, raw-device corners, or raw-device full sweep; return the exit code."""
  parser = argparse.ArgumentParser(description='Native, dependency-free SD/MMC capacity-fraud sweep (f3/h2testw style).')
  parser.add_argument('--dir', default=tempfile.gettempdir(), help='Directory on the card to sweep (default: system temp dir). Point this at the mounted card.')
  parser.add_argument('--device', default=None, help='DESTRUCTIVE quick mode: raw block device (e.g. /dev/disk4 or /dev/mmcblk0) to probe with a fast power-of-two "corners" sweep instead of filling free space. Overwrites the device. Needs --yes.')
  parser.add_argument('--full', action='store_true', help='With --device: exhaustive DESTRUCTIVE full-capacity sweep - write then verify EVERY block - instead of the fast corners probe. Needs no free space and catches arbitrary wraps corners can miss, but takes hours on a big card. Needs --yes.')
  parser.add_argument('--file-size-mb', type=int, default=DEFAULT_FILE_MB, help='Size of each test file in MiB (default: %(default)s)')
  parser.add_argument('--block-kb', type=int, default=DEFAULT_BLOCK_KB, help='IO/pattern block size in KiB (default: %(default)s)')
  parser.add_argument('--capacity-mb', type=int, default=None, help='Cap the free-space sweep, or override the probed capacity in --device mode, in MiB')
  parser.add_argument('--keep', action='store_true', help='Keep the test files instead of deleting them (free-space sweep only)')
  parser.add_argument('--yes', action='store_true', help='Confirm the DESTRUCTIVE raw write required by --device mode')
  parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON to stdout (progress on stderr)')
  args = parser.parse_args(argv)

  quiet = args.json

  # --full is a modifier on the raw-device mode; it means nothing without a device to sweep
  if args.full and args.device is None:
    sys.stderr.write('sdverify: --full requires --device (it is a raw-device sweep mode)\n')
    return 2

  # DESTRUCTIVE raw-device mode: fast corners probe by default, exhaustive full-capacity sweep with --full
  if args.device is not None:
    return _run_device_cli(args, quiet)

  # Default: non-destructive free-space fill sweep
  if not os.path.isdir(args.dir):
    sys.stderr.write('sdverify: --dir is not a directory: ' + args.dir + '\n')
    return 2

  cap = args.capacity_mb * 1024 * 1024 if args.capacity_mb is not None else None

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
