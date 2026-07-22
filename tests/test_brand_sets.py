# Tests for the brand-set signal derived from the CID table (src/rpi_sdinfo/cid_db.py). The model turns the
# free-text make/OEM brand lists into a countable set of brands observed shipping under each MID, and a structural
# validator gates it as the table grows. These tests pin the derivation (including the fiddly multi-brand / "or" /
# parenthetical / placeholder edge cases), that the shipped model stays clean, and that the validator actually
# rejects each fault class (a validator that never says no is worthless).
import _loader  # noqa: F401  (side effect: puts src/ on sys.path)
import unittest

from rpi_sdinfo import cid_db


class BrandsFromField(unittest.TestCase):
  def test_multi_brand_or_list(self):
    # The Phison OEM line: a comma list ending in "or", nine distinct brands, returned sorted.
    got = cid_db.brands_from_field('AgfaPhoto, Delkin, Integral, Lexar, Patriot, PNY, Polaroid, Sony, or Verbatim')
    # Sorted is ASCII order, so 'PNY' precedes 'Patriot' (uppercase N < lowercase a).
    self.assertEqual(got, ['AgfaPhoto', 'Delkin', 'Integral', 'Lexar', 'PNY', 'Patriot', 'Polaroid', 'Sony', 'Verbatim'])

  def test_two_brand_or(self):
    self.assertEqual(cid_db.brands_from_field('Gobe, or Sony'), ['Gobe', 'Sony'])
    self.assertEqual(cid_db.brands_from_field('Kingston, or SanDisk'), ['Kingston', 'SanDisk'])

  def test_or_inside_a_name_is_not_split(self):
    # \b anchors: "Corsair" / "Polaroid" contain the letters "or" but not the standalone word.
    self.assertEqual(cid_db.brands_from_field('AData, or Corsair'), ['AData', 'Corsair'])

  def test_parenthetical_qualifier_stripped_and_collapsed(self):
    # A grade qualifier is dropped so the same brand collapses across variants.
    self.assertEqual(cid_db.brands_from_field('Angelbird (V60), or Hoodman'), ['Angelbird', 'Hoodman'])
    self.assertEqual(cid_db.brands_from_field('Angelbird (V90)'), ['Angelbird'])

  def test_single_brand(self):
    self.assertEqual(cid_db.brands_from_field('SanDisk'), ['SanDisk'])
    self.assertEqual(cid_db.brands_from_field('Phison Electronics Corporation'), ['Phison Electronics Corporation'])

  def test_placeholder_dropped(self):
    self.assertEqual(cid_db.brands_from_field('Unknown'), [])
    self.assertEqual(cid_db.brands_from_field('unknown'), [])

  def test_empty_and_none(self):
    self.assertEqual(cid_db.brands_from_field(''), [])
    self.assertEqual(cid_db.brands_from_field(None), [])

  def test_duplicates_collapse(self):
    self.assertEqual(cid_db.brands_from_field('Lexar, PNY, or Lexar'), ['Lexar', 'PNY'])


class BrandSetsModel(unittest.TestCase):
  def test_mid_union_of_make_and_oem(self):
    # A MID whose make field and OEM line both name brands -> the MID set is their union; the OEM line is also
    # kept under by_oid for the finer MID/OID granularity.
    tree = {'SD': {'0x000027': {'manufacturer': 'Phison Electronics Corporation',
            '0x5048': {'oem': 'Lexar, PNY, or Sony'}}}}
    model = cid_db.brand_sets(tree)
    entry = model['SD']['0x000027']
    self.assertEqual(entry['brands'], ['Lexar', 'PNY', 'Phison Electronics Corporation', 'Sony'])
    self.assertEqual(entry['by_oid'], {'0x5048': ['Lexar', 'PNY', 'Sony']})

  def test_unknown_maker_absent(self):
    # A MID whose make is only a placeholder names no brand -> it does not appear in the model at all.
    tree = {'SD': {'0x000005': {'manufacturer': 'Unknown'}}}
    self.assertEqual(cid_db.brand_sets(tree), {})

  def test_product_only_mid_absent(self):
    # A MID with only product leaves (no make, no OEM line) yields no brand -> absent (neutral), never guessed.
    tree = {'SD': {'0x000012': {'0x5678': {'ASTC': {'0x3': {'label': 'Strontium 16 GB microSDHC C10'}}}}}}
    self.assertEqual(cid_db.brand_sets(tree), {})

  def test_empty_tree(self):
    self.assertEqual(cid_db.brand_sets({}), {})

  def test_oem_only_mid(self):
    # No make field, two OEM lines under different OIDs -> union across them, each kept in by_oid.
    tree = {'SD': {'0x00009c': {'0x534f': {'oem': 'Angelbird (V60), or Hoodman'},
            '0x4245': {'oem': 'Angelbird (V90)'}}}}
    entry = cid_db.brand_sets(tree)['SD']['0x00009c']
    self.assertEqual(entry['brands'], ['Angelbird', 'Hoodman'])
    self.assertEqual(entry['by_oid'], {'0x534f': ['Angelbird', 'Hoodman'], '0x4245': ['Angelbird']})


class BrandsObserved(unittest.TestCase):
  # brands_observed() reads the cached model derived from the *shipped* table.
  def test_known_mid_returns_sorted_brands(self):
    got = cid_db.brands_observed('SD', '0x000027')
    self.assertIn('Lexar', got)
    self.assertIn('Sony', got)
    self.assertEqual(got, sorted(got))

  def test_unknown_mid_is_empty(self):
    self.assertEqual(cid_db.brands_observed('SD', '0x0000ff'), [])

  def test_none_and_thin_are_empty(self):
    # No MID (macOS/Windows), a product-only MID, and an unknown-maker MID all read neutral.
    self.assertEqual(cid_db.brands_observed('SD', None), [])
    self.assertEqual(cid_db.brands_observed('SD', '0x000012'), [])  # product-only in the shipped table
    self.assertEqual(cid_db.brands_observed(None, None), [])

  def test_oid_narrows_when_present(self):
    # An OID present in the table narrows to that OEM line; an absent OID falls back to the whole-MID set.
    self.assertEqual(cid_db.brands_observed('SD', '0x00009c', '0x4245'), ['Angelbird'])
    self.assertEqual(cid_db.brands_observed('SD', '0x00009c', '0xffff'),
                     cid_db.brands_observed('SD', '0x00009c'))


class ValidatorCatchesFaults(unittest.TestCase):
  # Each case is a minimal model with exactly one planted fault; the validator must name it. The model is normally
  # derived (so a real parse never emits these), which is exactly why the validator guards against a derivation
  # regression - it is fed hand-built broken models here to prove it says no.
  def _has(self, problems, needle):
    self.assertTrue(any(needle in p for p in problems), 'expected a problem mentioning %r, got %r' % (needle, problems))

  def test_bad_mid_key(self):
    model = {'SD': {'0xZZZ': {'brands': ['SanDisk'], 'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'MID key')

  def test_bad_oid_key(self):
    model = {'SD': {'0x000003': {'brands': ['SanDisk'], 'by_oid': {'nothex': ['SanDisk']}}}}
    self._has(cid_db.validate_brand_sets(model), 'OID key')

  def test_top_level_must_be_sd_or_mmc(self):
    model = {'CF': {'0x000003': {'brands': ['SanDisk'], 'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'is not SD or MMC')

  def test_missing_brands(self):
    model = {'SD': {'0x000003': {'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'no brands set')

  def test_empty_brands_list(self):
    model = {'SD': {'0x000003': {'brands': [], 'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'must be a non-empty list')

  def test_placeholder_token(self):
    model = {'SD': {'0x000003': {'brands': ['Unknown'], 'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'placeholder')

  def test_separator_leak_token(self):
    # A comma or a standalone "or" surviving in a token means the parse leaked a whole list into one entry.
    model = {'SD': {'0x000003': {'brands': ['Lexar, PNY'], 'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'parse leak')

  def test_bracket_leak_token(self):
    model = {'SD': {'0x000003': {'brands': ['Angelbird (V90)'], 'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'parse leak')

  def test_empty_token(self):
    model = {'SD': {'0x000003': {'brands': [''], 'by_oid': {}}}}
    self._has(cid_db.validate_brand_sets(model), 'empty or not a string')

  def test_by_oid_not_a_dict(self):
    model = {'SD': {'0x000003': {'brands': ['SanDisk'], 'by_oid': ['SanDisk']}}}
    self._has(cid_db.validate_brand_sets(model), 'by_oid must be a dict')

  def test_clean_model_has_no_problems(self):
    model = {'SD': {'0x000027': {'brands': ['Lexar', 'PNY'], 'by_oid': {'0x5048': ['Lexar', 'PNY']}}}}
    self.assertEqual(cid_db.validate_brand_sets(model), [])


class ShippedModel(unittest.TestCase):
  def test_shipped_model_is_structurally_clean(self):
    # The derivation over the real table must never leak a separator, bracket, placeholder or empty token.
    problems = cid_db.validate_brand_sets()
    self.assertEqual(problems, [], 'shipped brand-set model has problems:\n' + '\n'.join(problems))

  def test_phison_brands_present(self):
    # The canonical case from ADR 0007: Phison's MID is observed shipping under many retail brands.
    brands = cid_db.brands_observed('SD', '0x000027')
    for expected in ('Lexar', 'PNY', 'Sony'):
      self.assertIn(expected, brands)


if __name__ == '__main__':
  unittest.main()
