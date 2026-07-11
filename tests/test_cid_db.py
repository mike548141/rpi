# Tests for the CID identity database and its structural validator (src/rpi_sdinfo/cid_db.py). The validator is
# what lets the crowd-sourced table grow safely: CI runs it over the shipped DB on every change, so a malformed
# contribution fails the build instead of silently breaking a lookup. These tests pin both that the shipped table
# is clean and that the validator actually rejects each fault class (a validator that never says no is worthless).
import _loader  # noqa: F401  (side effect: puts src/ on sys.path)
import unittest

from rpi_sdinfo import cid_db
from rpi_sdinfo.cli import speed_class


class ShippedDatabase(unittest.TestCase):
  def test_shipped_db_is_structurally_clean(self):
    # The whole point of the validator is to hold this true as the table grows - if it ever fails, the diff that
    # broke it should not merge.
    problems = cid_db.validate_cid_db(known_speed_classes=set(speed_class))
    self.assertEqual(problems, [], 'shipped CID DB has structural problems:\n' + '\n'.join(problems))

  def test_every_leaf_speed_class_token_is_known(self):
    # Belt-and-braces: the shipped DB must not reference a speed class the grader does not understand.
    problems = cid_db.validate_cid_db(known_speed_classes=set(speed_class))
    self.assertFalse(any('unknown speed_class' in p for p in problems))


class LeafCapacity(unittest.TestCase):
  def test_parses_gb_from_label(self):
    self.assertEqual(cid_db.leaf_capacity_bytes('SanDisk Ultra 64 GB microSDXC U1'), 64 * 1000 ** 3)

  def test_case_and_spacing_tolerant(self):
    self.assertEqual(cid_db.leaf_capacity_bytes('Team 32GB c10'), 32 * 1000 ** 3)

  def test_no_size_returns_none(self):
    self.assertIsNone(cid_db.leaf_capacity_bytes('ChromeBook Internal eMMC'))
    self.assertIsNone(cid_db.leaf_capacity_bytes(''))
    self.assertIsNone(cid_db.leaf_capacity_bytes(None))

  def test_mb_is_not_matched_as_gb(self):
    # A megabyte-sized legacy card must not be misread as that many GB.
    self.assertIsNone(cid_db.leaf_capacity_bytes('Ancient 512 MB SDSC'))


class ValidatorCatchesFaults(unittest.TestCase):
  # Each case is a minimal well-formed tree with exactly one planted fault; the validator must name it.
  def _has(self, problems, needle):
    self.assertTrue(any(needle in p for p in problems), 'expected a problem mentioning %r, got %r' % (needle, problems))

  def test_bad_mid_key(self):
    tree = {'SD': {'0xZZZ': {'manufacturer': 'Acme'}}}
    self._has(cid_db.validate_cid_db(tree), 'MID key')

  def test_bad_oid_key(self):
    tree = {'SD': {'0x000003': {'manufacturer': 'SanDisk', 'nothex': {'oem': 'SanDisk'}}}}
    self._has(cid_db.validate_cid_db(tree), 'OID key')

  def test_bad_prv_key(self):
    tree = {'SD': {'0x000003': {'0x5344': {'SD02G': {'8': {'label': 'x 2 GB'}}}}}}
    self._has(cid_db.validate_cid_db(tree), 'hwrev key')

  def test_leaf_without_identity(self):
    tree = {'SD': {'0x000003': {'0x5344': {'SD02G': {'0x8': {'speed_class': ['C10']}}}}}}
    self._has(cid_db.validate_cid_db(tree), 'neither label nor alternate')

  def test_unknown_speed_class_token(self):
    tree = {'SD': {'0x000003': {'0x5344': {'SD02G': {'0x8': {'label': 'x 2 GB', 'speed_class': ['Z99']}}}}}}
    self._has(cid_db.validate_cid_db(tree, known_speed_classes={'C10', 'U1'}), 'unknown speed_class')

  def test_speed_class_not_a_list(self):
    tree = {'SD': {'0x000003': {'0x5344': {'SD02G': {'0x8': {'label': 'x 2 GB', 'speed_class': 'C10'}}}}}}
    self._has(cid_db.validate_cid_db(tree), 'speed_class must be a list')

  def test_capacity_bytes_disagrees_with_label(self):
    tree = {'SD': {'0x000003': {'0x5344': {'SD64G': {'0x8': {'label': 'x 64 GB', 'capacity_bytes': 32 * 1000 ** 3}}}}}}
    self._has(cid_db.validate_cid_db(tree), 'disagrees with the label size')

  def test_top_level_must_be_sd_or_mmc(self):
    tree = {'CF': {'0x000003': {'manufacturer': 'SanDisk'}}}
    self._has(cid_db.validate_cid_db(tree), 'is not SD or MMC')

  def test_empty_manufacturer_string(self):
    tree = {'SD': {'0x000003': {'manufacturer': ''}}}
    self._has(cid_db.validate_cid_db(tree), 'manufacturer must be a non-empty string')

  def test_clean_tree_has_no_problems(self):
    tree = {'SD': {'0x000003': {'manufacturer': 'SanDisk', '0x5344': {'oem': 'SanDisk',
            'SD02G': {'0x8': {'label': 'SanDisk Blue 2 GB SDSC', 'speed_class': ['C10']}}}}}}
    self.assertEqual(cid_db.validate_cid_db(tree, known_speed_classes={'C10'}), [])


if __name__ == '__main__':
  unittest.main()
