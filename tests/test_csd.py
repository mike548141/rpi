# CSD register decode + CID/CSD cross-checks - the metadata-only fake detection.
# These are pure logic and hardware-independent, so they are the highest-value things to lock in.
import unittest

from _loader import build_csd, csize_for_capacity_v2, load_sdinfo

sdinfo = load_sdinfo()


class DecodeCsdRoundTrip(unittest.TestCase):
  def test_sdsc_v1_capacity(self):
    # v1.0: capacity = (c_size + 1) * 2**(c_size_mult + 2) * 2**read_bl_len
    hexstr = build_csd(0, read_bl_len=9, c_size=4095, c_size_mult=7)
    d = sdinfo.decode_csd(hexstr)
    self.assertEqual(d['structure'], 0)
    self.assertEqual(d['capacity_type'], 'SDSC')
    self.assertEqual(d['read_bl_len'], 9)
    self.assertEqual(d['capacity_bytes'], (4095 + 1) * (1 << (7 + 2)) * (1 << 9))

  def test_sdhc_v2_capacity_and_type(self):
    # 8 GB -> below the 32e9 SDXC boundary, so it must classify as SDHC
    c_size = csize_for_capacity_v2(8 * 1024 ** 3)
    d = sdinfo.decode_csd(build_csd(1, c_size=c_size))
    self.assertEqual(d['structure'], 1)
    self.assertEqual(d['capacity_type'], 'SDHC')
    self.assertEqual(d['capacity_bytes'], (c_size + 1) * 512 * 1024)

  def test_sdxc_v2_type_boundary(self):
    # 64 GB is above 32e9, so the same v2.0 structure classifies as SDXC
    c_size = csize_for_capacity_v2(64 * 1024 ** 3)
    d = sdinfo.decode_csd(build_csd(1, c_size=c_size))
    self.assertEqual(d['capacity_type'], 'SDXC')

  def test_sduc_v3(self):
    c_size = csize_for_capacity_v2(1024 * 1024 ** 3)
    d = sdinfo.decode_csd(build_csd(2, c_size=c_size))
    self.assertEqual(d['structure'], 2)
    self.assertEqual(d['capacity_type'], 'SDUC')

  def test_tran_speed_codes(self):
    # 0x32 is the legacy 25 Mbit/s default; 0x5A is high-speed 50 Mbit/s
    self.assertEqual(sdinfo.decode_csd(build_csd(1, tran_speed=0x32, c_size=100))['tran_speed_mbit'], 25.0)
    self.assertEqual(sdinfo.decode_csd(build_csd(1, tran_speed=0x5A, c_size=100))['tran_speed_mbit'], 50.0)

  def test_malformed_returns_none(self):
    for bad in (None, '', 'zz', 'abc', '0' * 31, '0' * 33, 'x' * 32):
      self.assertIsNone(sdinfo.decode_csd(bad))

  def test_accepts_colon_and_space_formatting(self):
    hexstr = build_csd(1, c_size=csize_for_capacity_v2(8 * 1024 ** 3))
    spaced = ' '.join(hexstr[i:i + 2] for i in range(0, 32, 2))
    coloned = ':'.join(hexstr[i:i + 2] for i in range(0, 32, 2))
    self.assertEqual(sdinfo.decode_csd(spaced)['capacity_bytes'],
                     sdinfo.decode_csd(hexstr)['capacity_bytes'])
    self.assertEqual(sdinfo.decode_csd(coloned)['capacity_bytes'],
                     sdinfo.decode_csd(hexstr)['capacity_bytes'])


class CrossCheck(unittest.TestCase):
  def _storage(self, csd_hex, reported_bytes, **extra):
    storage = {'csd_decoded': sdinfo.decode_csd(csd_hex), 'bytes': reported_bytes}
    storage.update(extra)
    return storage

  def test_reflashed_fake_fails(self):
    # The headline signature: a Standard-Capacity (v1.0) CSD on a card claiming 64 GB is impossible
    small = build_csd(0, c_size=4095, c_size_mult=7, read_bl_len=9)  # ~1 GiB real
    findings = sdinfo.cross_check(self._storage(small, 64 * 1000 ** 3))
    self.assertTrue(any(f['severity'] == 'fail' for f in findings))

  def test_genuine_card_no_fail(self):
    c_size = csize_for_capacity_v2(32 * 1024 ** 3)
    genuine = build_csd(1, c_size=c_size)
    findings = sdinfo.cross_check(self._storage(genuine, (c_size + 1) * 512 * 1024))
    self.assertFalse(any(f['severity'] == 'fail' for f in findings))

  def test_sdsc_over_2gb_warns_not_fails(self):
    # Between 2 and 4 GB on a v1.0 CSD is suspicious (warn) but not physically impossible (no fail)
    small = build_csd(0, c_size=4095, c_size_mult=7, read_bl_len=9)
    findings = sdinfo.cross_check(self._storage(small, 3 * 1000 ** 3))
    self.assertTrue(any(f['severity'] == 'warn' for f in findings))
    self.assertFalse(any(f['severity'] == 'fail' for f in findings))

  def test_capacity_mismatch_warns(self):
    c_size = csize_for_capacity_v2(32 * 1024 ** 3)
    genuine = build_csd(1, c_size=c_size)
    # Report a capacity 20% larger than the CSD says -> a mismatch warning
    findings = sdinfo.cross_check(self._storage(genuine, int((c_size + 1) * 512 * 1024 * 1.2)))
    self.assertTrue(any(f['severity'] == 'warn' for f in findings))

  def test_future_manufacturing_date_warns(self):
    c_size = csize_for_capacity_v2(32 * 1024 ** 3)
    genuine = build_csd(1, c_size=c_size)
    storage = self._storage(genuine, (c_size + 1) * 512 * 1024, cid_mdt='06/2030')
    findings = sdinfo.cross_check(storage, now=(2026, 7))
    self.assertTrue(any('future' in f['message'] for f in findings))

  def test_unknown_make_is_info_only(self):
    c_size = csize_for_capacity_v2(32 * 1024 ** 3)
    genuine = build_csd(1, c_size=c_size)
    storage = self._storage(genuine, (c_size + 1) * 512 * 1024,
                            cid_pnm='SD32G', manufacturer='unknown')
    findings = sdinfo.cross_check(storage)
    infos = [f for f in findings if f['severity'] == 'info']
    self.assertTrue(infos)
    self.assertFalse(any(f['severity'] == 'fail' for f in findings))


class MalformedCsd(unittest.TestCase):
  # Structural-validity liar-checks: a genuine SD controller emits a spec-valid CSD, so garbage in these fields
  # is a counterfeit tell. These are warns (strong hints), not fails, and must never fire on a genuine card.
  def _storage(self, csd_hex, reported=32 * 1000 ** 3):
    return {'csd_decoded': sdinfo.decode_csd(csd_hex), 'bytes': reported}

  def _msgs(self, storage):
    return ' | '.join(f['message'] for f in sdinfo.cross_check(storage) if f['severity'] == 'warn')

  def test_genuine_card_has_no_structural_warnings(self):
    c_size = csize_for_capacity_v2(32 * 1024 ** 3)
    genuine = build_csd(1, c_size=c_size)                     # default ccc/tran_speed/read_bl_len are all valid
    msgs = self._msgs(self._storage(genuine, (c_size + 1) * 512 * 1024))
    for term in ('reserved', 'TRAN_SPEED', 'command', 'READ_BL_LEN'):
      self.assertNotIn(term, msgs)

  def test_reserved_structure_version_warns(self):
    self.assertIn('reserved', self._msgs(self._storage(build_csd(3, c_size=100))))

  def test_zero_tran_speed_warns(self):
    self.assertIn('TRAN_SPEED', self._msgs(self._storage(build_csd(1, tran_speed=0, c_size=100))))

  def test_empty_command_classes_warns(self):
    self.assertIn('command-classes field is empty', self._msgs(self._storage(build_csd(1, ccc=0, c_size=100))))

  def test_missing_mandatory_command_class_warns(self):
    ccc = 0x5B5 & ~(1 << 4)                                   # drop class 4 (block write) from the standard set
    self.assertIn('mandatory command class', self._msgs(self._storage(build_csd(1, ccc=ccc, c_size=100))))

  def test_illegal_read_bl_len_warns(self):
    bad = build_csd(0, read_bl_len=15, c_size=100, c_size_mult=0)
    self.assertIn('READ_BL_LEN', self._msgs(self._storage(bad)))

  def test_no_fail_from_structural_checks(self):
    # Structural malformations are strong hints, not exit-code failures - keep them at warn severity
    for csd in (build_csd(3, c_size=100), build_csd(1, tran_speed=0, c_size=100), build_csd(1, ccc=0, c_size=100)):
      findings = sdinfo.cross_check(self._storage(csd))
      self.assertFalse(any(f['severity'] == 'fail' for f in findings))


class BusCeilingNote(unittest.TestCase):
  # A genuine high-class card on a default/high-speed bus is NOT a fake, but the gap between its rating and the
  # bus it can advertise is surfaced as info so the user understands a real card measuring below its label.
  def _findings(self, tran_speed, speed_class):
    c_size = csize_for_capacity_v2(32 * 1024 ** 3)
    storage = {'csd_decoded': sdinfo.decode_csd(build_csd(1, tran_speed=tran_speed, c_size=c_size)),
               'bytes': (c_size + 1) * 512 * 1024, 'speed_class': speed_class}
    return sdinfo.cross_check(storage)

  def test_u3_on_high_speed_bus_gets_info_not_warn_or_fail(self):
    findings = self._findings(0x5A, ['U3', 'C10'])           # rated 30 MB/s, HS bus ~25 MB/s ceiling
    self.assertTrue(any(f['severity'] == 'info' and 'bus-limited' in f['message'] for f in findings))
    self.assertFalse(any(f['severity'] in ('warn', 'fail') for f in findings))

  def test_message_names_rated_and_ceiling(self):
    msg = next(f['message'] for f in self._findings(0x5A, ['V30']) if f['severity'] == 'info')
    self.assertIn('30 MB/s', msg)                            # the rated floor
    self.assertIn('25 MB/s', msg)                            # the high-speed bus ceiling

  def test_default_speed_bus_names_itself(self):
    msg = next(f['message'] for f in self._findings(0x32, ['U3']) if f['severity'] == 'info')
    self.assertIn('default-speed', msg)                      # 25 Mbit/s -> ~12.5 MB/s ceiling
    self.assertIn('12.5 MB/s', msg)

  def test_class10_within_bus_ceiling_no_note(self):
    # C10/U1 need 10 MB/s; a high-speed bus clears ~25 MB/s, so there is nothing to explain
    findings = self._findings(0x5A, ['C10', 'U1'])
    self.assertFalse(any('bus-limited' in f['message'] for f in findings))

  def test_unknown_class_no_note(self):
    # macOS/Windows or an unrecognised card has no rated class, so there is no floor to compare against
    self.assertFalse(any('bus-limited' in f['message'] for f in self._findings(0x32, [])))


class RatedWriteFloor(unittest.TestCase):
  def test_takes_the_highest_class(self):
    self.assertEqual(sdinfo._rated_write_floor(['C10', 'U3']), 30)
    self.assertEqual(sdinfo._rated_write_floor(['A1', 'V90']), 90)

  def test_unknown_and_empty(self):
    self.assertEqual(sdinfo._rated_write_floor([]), 0)
    self.assertEqual(sdinfo._rated_write_floor(['bogus']), 0)
    self.assertEqual(sdinfo._rated_write_floor(None), 0)


class ParseMdt(unittest.TestCase):
  def test_valid(self):
    self.assertEqual(sdinfo._parse_mdt('06/2024'), (2024, 6))

  def test_invalid(self):
    for bad in (None, '', 'garbage', '2024', '13-2024'):
      self.assertIsNone(sdinfo._parse_mdt(bad))


if __name__ == '__main__':
  unittest.main()
