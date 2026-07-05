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


class ParseMdt(unittest.TestCase):
  def test_valid(self):
    self.assertEqual(sdinfo._parse_mdt('06/2024'), (2024, 6))

  def test_invalid(self):
    for bad in (None, '', 'garbage', '2024', '13-2024'):
      self.assertIsNone(sdinfo._parse_mdt(bad))


if __name__ == '__main__':
  unittest.main()
