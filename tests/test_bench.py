# sdbench pure-maths: the hand-rolled percentile helper (kept off statistics.quantiles for the 3.6
# floor) and the latency distribution built on top of it.
import os
import tempfile
import unittest

import _loader  # noqa: F401 - puts src/ on sys.path so rpi_sdinfo imports
from rpi_sdinfo import bench as sdbench


class Percentile(unittest.TestCase):
  def test_extremes(self):
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    self.assertEqual(sdbench._percentile(vals, 0), 1.0)
    self.assertEqual(sdbench._percentile(vals, 100), 5.0)

  def test_median_interpolation(self):
    self.assertEqual(sdbench._percentile([1.0, 2.0, 3.0, 4.0], 50), 2.5)

  def test_linear_interpolation_between_ranks(self):
    # 25th percentile of [0,10] -> rank 0.25 -> 2.5
    self.assertAlmostEqual(sdbench._percentile([0.0, 10.0], 25), 2.5)

  def test_single_and_empty(self):
    self.assertEqual(sdbench._percentile([7.0], 95), 7.0)
    self.assertEqual(sdbench._percentile([], 95), 0.0)

  def test_monotonic_ordering(self):
    vals = sorted(float(x) for x in range(1, 101))
    p50 = sdbench._percentile(vals, 50)
    p95 = sdbench._percentile(vals, 95)
    p99 = sdbench._percentile(vals, 99)
    self.assertLessEqual(p50, p95)
    self.assertLessEqual(p95, p99)


class LatencyStats(unittest.TestCase):
  def test_converts_seconds_to_ms(self):
    stats = sdbench._latency_stats([0.001, 0.002, 0.003])  # 1, 2, 3 ms
    self.assertAlmostEqual(stats['mean_ms'], 2.0)
    self.assertAlmostEqual(stats['min_ms'], 1.0)
    self.assertAlmostEqual(stats['max_ms'], 3.0)
    self.assertAlmostEqual(stats['p50_ms'], 2.0)

  def test_empty_is_all_zero(self):
    stats = sdbench._latency_stats([])
    self.assertEqual(set(stats.values()), {0.0})

  def test_keys_present(self):
    stats = sdbench._latency_stats([0.001])
    self.assertEqual(set(stats), {'mean_ms', 'p50_ms', 'p95_ms', 'p99_ms', 'min_ms', 'max_ms'})


class ResultPackaging(unittest.TestCase):
  def test_result_mbps_and_iops(self):
    # 10 MB in 1 s across 10 ops -> 10 MBps, 10 IOPS
    r = sdbench._result(10_000_000, 10, 1.0, [0.1] * 10)
    self.assertAlmostEqual(r['mbps'], 10.0)
    self.assertAlmostEqual(r['iops'], 10.0)
    self.assertAlmostEqual(r['lat_ms'], 100.0)
    self.assertIn('lat', r)

  def test_zero_elapsed_guarded(self):
    r = sdbench._result(1000, 5, 0.0, [])
    self.assertEqual(r['mbps'], 0.0)
    self.assertEqual(r['iops'], 0.0)

  def test_empty_results_shape(self):
    empty = sdbench.empty_results()
    self.assertIn('write', empty)
    self.assertIn('read', empty)


class SweepBlocks(unittest.TestCase):
  def test_full_range_survives_large_file(self):
    # A file bigger than the largest block keeps every requested block size
    blocks = sdbench._sweep_blocks(64 * 1024 * 1024)
    self.assertEqual(blocks, list(sdbench.SWEEP_BLOCKS))

  def test_clamps_and_dedups_small_file(self):
    # A 32 KiB file collapses 64 KiB/256 KiB/1 MiB into a single 32 KiB pass, keeping 4/16/32
    blocks = sdbench._sweep_blocks(32 * 1024)
    self.assertEqual(blocks, [4 * 1024, 16 * 1024, 32 * 1024])

  def test_tiny_file_is_single_pass(self):
    self.assertEqual(sdbench._sweep_blocks(1024), [1024])

  def test_sorted_ascending(self):
    blocks = sdbench._sweep_blocks(1024 * 1024, block_sizes=(1024 * 1024, 4 * 1024, 64 * 1024))
    self.assertEqual(blocks, sorted(blocks))


class FmtBlock(unittest.TestCase):
  def test_kib_and_mib(self):
    self.assertEqual(sdbench._fmt_block(4 * 1024), '4 KiB')
    self.assertEqual(sdbench._fmt_block(256 * 1024), '256 KiB')
    self.assertEqual(sdbench._fmt_block(1024 * 1024), '1 MiB')
    self.assertEqual(sdbench._fmt_block(2 * 1024 * 1024), '2 MiB')


class BlockSizeSweep(unittest.TestCase):
  def test_one_entry_per_block_over_real_file(self):
    # Small real IO: a 256 KiB file swept with three block sizes yields three well-formed entries
    fd, path = tempfile.mkstemp()
    os.close(fd)
    try:
      sizes = (4 * 1024, 64 * 1024, 256 * 1024)
      sweep = sdbench.block_size_sweep(path, 256 * 1024, block_sizes=sizes)
      self.assertEqual([e['block_bytes'] for e in sweep], list(sizes))
      for entry in sweep:
        self.assertIn('mbps', entry)
        self.assertIn('lat', entry)
        self.assertGreaterEqual(entry['mbps'], 0.0)
    finally:
      os.remove(path)

  def test_phase_callback_fires_per_block(self):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    seen = []
    try:
      sdbench.block_size_sweep(path, 128 * 1024, block_sizes=(4 * 1024, 128 * 1024), on_phase=seen.append)
    finally:
      os.remove(path)
    self.assertEqual(seen, [4 * 1024, 128 * 1024])


if __name__ == '__main__':
  unittest.main()
