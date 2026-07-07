# sdverify pure logic: the offset-keyed pattern, the corners-probe set, and - the important one - a
# simulated power-of-two address-truncation fake, proving the (0, R) alias is always caught.
import shutil
import tempfile
import unittest

import _loader  # noqa: F401 - puts src/ on sys.path so rpi_sdinfo imports
from rpi_sdinfo import verify as sdverify


class PatternBlock(unittest.TestCase):
  def test_deterministic(self):
    self.assertEqual(sdverify.pattern_block(4096, 64), sdverify.pattern_block(4096, 64))

  def test_length_honoured(self):
    self.assertEqual(len(sdverify.pattern_block(0, 137)), 137)

  def test_offset_unique(self):
    # Different offsets must yield different bytes, or a wrapping fake could go undetected
    self.assertNotEqual(sdverify.pattern_block(0, 64), sdverify.pattern_block(512, 64))

  def test_not_trivially_compressible(self):
    block = sdverify.pattern_block(1 << 20, 256)
    self.assertGreater(len(set(block)), 100)  # high byte diversity


class CornerOffsets(unittest.TestCase):
  def test_includes_zero_last_and_powers_of_two(self):
    offsets = sdverify.corner_offsets(4096, 512)
    self.assertIn(0, offsets)
    self.assertIn(3584, offsets)              # last full block
    for p in (512, 1024, 2048):
      self.assertIn(p, offsets)
    self.assertEqual(offsets, sorted(offsets))

  def test_tiny_capacity(self):
    self.assertEqual(sdverify.corner_offsets(256, 512), [0])

  def test_includes_common_decimal_boundaries(self):
    # A large reported capacity must also probe the non-power-of-two decimal capacity boundaries below it,
    # so a fake that wraps at a round decimal size (with no power-of-two structure) is still caught.
    block = sdverify.DEFAULT_BLOCK_KB * 1024
    offsets = sdverify.corner_offsets(512 * 1000 * 1000 * 1000, block)
    for boundary in (8 * 1000 * 1000 * 1000, 100 * 1000 * 1000 * 1000, 256 * 1000 * 1000 * 1000):
      self.assertIn(boundary, offsets)
    # Boundaries at or above the reported capacity are not probed (they are not a wrap *below* it)
    self.assertNotIn(512 * 1000 * 1000 * 1000, offsets)

  def test_decimal_boundaries_are_512_aligned(self):
    # Probing the exact boundary only stays legal for raw-device I/O if it is block-aligned; every n*10^9 is
    for boundary in sdverify.COMMON_FAKE_CAPACITIES_BYTES:
      self.assertEqual(boundary % 512, 0)


class FakeDevice:
  # A counterfeit that truncates the block address at `wrap` bytes: every access aliases modulo wrap,
  # so a high offset silently lands on a low physical cell. wrap=None models a genuine device.
  def __init__(self, wrap=None):
    self.store = {}
    self.wrap = wrap

  def _phys(self, offset):
    return offset % self.wrap if self.wrap else offset

  def pwrite(self, offset, data):
    self.store[self._phys(offset)] = data

  def pread(self, offset, length):
    return self.store.get(self._phys(offset), b'\x00' * length)[:length]


class CornersSweepDetection(unittest.TestCase):
  def _sweep(self, wrap):
    cap, block = 4096, 512
    dev = FakeDevice(wrap=wrap)
    offsets = sdverify.corner_offsets(cap, block)
    sdverify.write_offsets(dev.pwrite, offsets, block, cap)
    return sdverify.verify_offsets(dev.pread, offsets, block, cap)

  def test_genuine_device_verifies_clean(self):
    good, first_bad = self._sweep(wrap=None)
    self.assertIsNone(first_bad)

  def test_power_of_two_wrap_is_caught(self):
    # Wrap at 2048 (a power-of-two boundary in the probe set): offset 2048 aliases onto 0,
    # overwriting block 0's pattern, so the read-back of 0 must mismatch.
    good, first_bad = self._sweep(wrap=2048)
    self.assertIsNotNone(first_bad)

  def test_non_power_of_two_decimal_wrap_is_caught(self):
    # A fake with a real 8 GB chip reporting 512 GB wraps at a non-power-of-two boundary. The congruence-
    # busting decimal probe at 8e9 aliases onto block 0, so the sweep must flag it. (Big offsets, but the
    # FakeDevice keys physical writes in a dict, so only the ~30 probed blocks are ever materialised.)
    cap, block = 512 * 1000 * 1000 * 1000, sdverify.DEFAULT_BLOCK_KB * 1024
    wrap = 8 * 1000 * 1000 * 1000
    dev = FakeDevice(wrap=wrap)
    offsets = sdverify.corner_offsets(cap, block)
    self.assertIn(wrap, offsets)                       # the busting probe is present...
    sdverify.write_offsets(dev.pwrite, offsets, block, cap)
    good, first_bad = sdverify.verify_offsets(dev.pread, offsets, block, cap)
    self.assertIsNotNone(first_bad)                    # ...and the wrap is caught


class PlanSweep(unittest.TestCase):
  def test_leaves_a_safety_margin(self):
    tmp = tempfile.mkdtemp()
    try:
      sweep, usage = sdverify.plan_sweep(tmp)
      self.assertLess(sweep, usage.free)         # never fills to the brim
      self.assertGreaterEqual(sweep, 0)
    finally:
      shutil.rmtree(tmp)

  def test_capacity_cap_applied(self):
    tmp = tempfile.mkdtemp()
    try:
      sweep, _ = sdverify.plan_sweep(tmp, capacity_bytes=1024)
      self.assertLessEqual(sweep, 1024)
    finally:
      shutil.rmtree(tmp)


if __name__ == '__main__':
  unittest.main()
