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
