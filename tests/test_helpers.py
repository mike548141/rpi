# Small parsing / maths helpers in rpi-sdinfo. Fragile-parsing bugs here caused real 0.3 crashes,
# so pin the behaviour down.
import os
import tempfile
import unittest

from _loader import load_sdinfo

sdinfo = load_sdinfo()


class ParseKv(unittest.TestCase):
  def test_label_lookup(self):
    lines = ['Filesystem state:  clean', 'Mount count:   7', 'garbage line', 'Last checked: never']
    kv = sdinfo.parse_kv(lines)
    self.assertEqual(kv['Filesystem state'], 'clean')
    self.assertEqual(kv['Mount count'], '7')
    self.assertEqual(kv['Last checked'], 'never')
    self.assertNotIn('garbage line', kv)

  def test_only_first_separator_splits(self):
    kv = sdinfo.parse_kv(['Last mount time: Wed 12:00:00 2024'])  # leakscan:allow: '12:00:00' is a clock time in a dumpe2fs fixture, not an IPv6 address
    self.assertEqual(kv['Last mount time'], 'Wed 12:00:00 2024')  # leakscan:allow: '12:00:00' is a clock time in a dumpe2fs fixture, not an IPv6 address

  def test_custom_separator(self):
    self.assertEqual(sdinfo.parse_kv(['a=1', 'b=2'], separator='=')['b'], '2')


class Mib(unittest.TestCase):
  def test_kb_to_mib(self):
    self.assertEqual(sdinfo.mib('1048576 kB'), 1024.0)

  def test_bare_number(self):
    self.assertEqual(sdinfo.mib('2048'), 2.0)


class SafeDiv(unittest.TestCase):
  def test_normal(self):
    self.assertEqual(sdinfo.safe_div(10, 2), 5)

  def test_zero_denominator(self):
    self.assertEqual(sdinfo.safe_div(10, 0), 0)


class BestMedian(unittest.TestCase):
  def test_higher_is_better_drops_slow_half(self):
    # Best half of [1,2,3,4] (higher better) is [3,4] -> median 3.5
    self.assertEqual(sdinfo.best_median([1, 2, 3, 4]), 3.5)

  def test_lower_is_better_drops_high_half(self):
    # Best (lowest) half of [1,2,3,4] is [1,2] -> median 1.5
    self.assertEqual(sdinfo.best_median([1, 2, 3, 4], higher_is_better=False), 1.5)

  def test_single_value(self):
    self.assertEqual(sdinfo.best_median([5]), 5)
    self.assertEqual(sdinfo.best_median([5], higher_is_better=False), 5)


class ResolveBlockSize(unittest.TestCase):
  def test_normal_block_addressed(self):
    self.assertEqual(sdinfo.resolve_block_size(512), (512, False))
    self.assertEqual(sdinfo.resolve_block_size('512'), (512, False))

  def test_zero_falls_back_and_flags(self):
    # erase_size 0 => not block-addressed => assume 512 and report the assumption
    self.assertEqual(sdinfo.resolve_block_size(0), (512, True))
    self.assertEqual(sdinfo.resolve_block_size(''), (512, True))
    self.assertEqual(sdinfo.resolve_block_size(None), (512, True))

  def test_garbage_falls_back(self):
    self.assertEqual(sdinfo.resolve_block_size('nope'), (512, True))


class Lookup(unittest.TestCase):
  TREE = {'SD': {'0x03': {'manufacturer': 'SanDisk', '0x5344': {'oem': 'SD'}}}}

  def test_hit(self):
    self.assertEqual(sdinfo._lookup(self.TREE, 'SD', '0x03', 'manufacturer'), 'SanDisk')

  def test_missing_key_returns_default(self):
    self.assertEqual(sdinfo._lookup(self.TREE, 'SD', '0xff', 'manufacturer', default='unknown'), 'unknown')

  def test_non_dict_intermediate_returns_default(self):
    # 'manufacturer' is a string; descending past it must yield the default, not a TypeError
    self.assertEqual(sdinfo._lookup(self.TREE, 'SD', '0x03', 'manufacturer', 'deeper', default=[]), [])

  def test_deep_hit(self):
    self.assertEqual(sdinfo._lookup(self.TREE, 'SD', '0x03', '0x5344', 'oem'), 'SD')


class CrossCheckBlockSize(unittest.TestCase):
  def test_assumed_block_size_is_info(self):
    findings = sdinfo.cross_check({'block_size_assumed': True, 'bytes': 0})
    self.assertTrue(any(f['severity'] == 'info' and 'block-addressed' in f['message'] for f in findings))

  def test_normal_block_size_no_finding(self):
    findings = sdinfo.cross_check({'block_size_assumed': False, 'bytes': 0})
    self.assertFalse(any('block-addressed' in f['message'] for f in findings))


class ReadFile(unittest.TestCase):
  def test_missing_returns_empty_string(self):
    self.assertEqual(sdinfo.read_file('/no/such/path/at/all'), '')

  def test_unreadable_returns_empty_not_traceback(self):
    # A node that exists but is permission-gated (like the root-only Bluetooth identity) must degrade
    # to '' rather than raising - the tool should never traceback on an unreadable sysfs node
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as fh:
      fh.write('secret')
      path = fh.name
    os.chmod(path, 0o000)
    try:
      # Verify the precondition rather than assuming a platform can establish it. chmod 0o000 does not deny
      # reads for root, nor on Windows (tier 2), where it only toggles the read-only flag. Skipping on the
      # observed fact beats guessing from sys.platform - and keeps the assertion honest wherever it does run.
      try:
        with open(path) as fh:
          fh.read()
        self.skipTest('cannot make a file unreadable here (root, or Windows chmod semantics)')
      except PermissionError:
        pass
      self.assertEqual(sdinfo.read_file(path), '')
    finally:
      os.chmod(path, 0o600)
      os.unlink(path)

  def test_all_scope_strips_search_token(self):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as fh:
      fh.write('serial\x00number\x00')
      path = fh.name
    try:
      self.assertEqual(sdinfo.read_file(path, '\x00'), 'serialnumber')
    finally:
      os.unlink(path)

  def test_regex_scope_returns_matching_lines(self):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as fh:
      fh.write('alpha 1\nbeta 2\nalpha 3\n')
      path = fh.name
    try:
      out = sdinfo.read_file(path, 'alpha', 'regex')
      self.assertEqual(out, 'alpha 1\nalpha 3\n')
    finally:
      os.unlink(path)

  def _write(self, text):
    fh = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    fh.write(text)
    fh.close()
    self.addCleanup(os.unlink, fh.name)
    return fh.name

  def test_lines_scope_single_index(self):
    path = self._write('one\ntwo\nthree\n')
    self.assertEqual(sdinfo.read_file(path, 0, 'lines'), 'one\n')
    self.assertEqual(sdinfo.read_file(path, -1, 'lines'), 'three\n')

  def test_lines_scope_out_of_range_index_is_empty(self):
    # Out-of-range must degrade to '' (the no-traceback contract), not raise IndexError
    path = self._write('one\ntwo\n')
    self.assertEqual(sdinfo.read_file(path, 9, 'lines'), '')

  def test_lines_scope_range_tuple(self):
    path = self._write('one\ntwo\nthree\nfour\n')
    self.assertEqual(sdinfo.read_file(path, (1, 3), 'lines'), 'two\nthree\n')

  def test_lines_scope_range_slice_and_step(self):
    path = self._write('one\ntwo\nthree\nfour\n')
    self.assertEqual(sdinfo.read_file(path, slice(None, None, 2), 'lines'), 'one\nthree\n')

  def test_lines_scope_range_clamps_past_end(self):
    # A slice past the end clamps (no exception), unlike a bad int index
    path = self._write('one\ntwo\n')
    self.assertEqual(sdinfo.read_file(path, (1, 99), 'lines'), 'two\n')

  def test_lines_scope_no_selector_returns_whole_file(self):
    path = self._write('one\ntwo\n')
    self.assertEqual(sdinfo.read_file(path, return_scope='lines'), 'one\ntwo\n')


if __name__ == '__main__':
  unittest.main()
