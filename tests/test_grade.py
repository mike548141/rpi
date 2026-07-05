# compute_grade: PASS/FAIL against the toughest target implied by the declared speed class(es),
# with an A1 fallback for any metric a class does not specify.
import unittest

from _loader import load_sdinfo

sdinfo = load_sdinfo()


def sys_info(seq_write, rand_write_iops, rand_read_iops, classes):
  return {
    'perf': {
      'write': {'seq_mbps_result': seq_write, 'rand_4kb_iops_result': rand_write_iops},
      'read': {'rand_4kb_iops_result': rand_read_iops},
    },
    'storage': {'speed_class': classes},
  }


class ComputeGrade(unittest.TestCase):
  def test_no_class_falls_back_to_a1(self):
    grade = sdinfo.compute_grade(sys_info(20, 600, 2000, []))
    self.assertTrue(grade['assumed'])
    self.assertEqual(grade['graded_against'], 'A1')
    self.assertEqual(grade['targets']['seq_write'], 10)     # A1 seq_write
    self.assertEqual(grade['targets']['rand_read'], 1500)   # A1 rand_read
    self.assertTrue(grade['pass'])

  def test_slow_card_fails_overall(self):
    # Meets seq + rand_write but misses A1's 1500 rand_read IOPS -> overall fail
    grade = sdinfo.compute_grade(sys_info(20, 600, 1000, []))
    self.assertFalse(grade['metrics']['rand_read']['pass'])
    self.assertFalse(grade['pass'])

  def test_toughest_of_multiple_classes(self):
    # V30 (seq 30) + A2 (rand_read 4000 / rand_write 2000) -> targets take the max of each
    grade = sdinfo.compute_grade(sys_info(35, 2500, 4500, ['V30', 'A2']))
    self.assertEqual(grade['targets']['seq_write'], 30)
    self.assertEqual(grade['targets']['rand_read'], 4000)
    self.assertEqual(grade['targets']['rand_write'], 2000)
    self.assertFalse(grade['assumed'])
    self.assertTrue(grade['pass'])

  def test_seq_only_class_fills_random_from_a1(self):
    # V30 declares only seq_write; rand targets must fall back to A1 (1500 / 500)
    grade = sdinfo.compute_grade(sys_info(35, 600, 2000, ['V30']))
    self.assertEqual(grade['targets']['rand_read'], 1500)
    self.assertEqual(grade['targets']['rand_write'], 500)
    self.assertTrue(grade['pass'])

  def test_boundary_measured_equals_target_passes(self):
    grade = sdinfo.compute_grade(sys_info(10, 500, 1500, []))
    self.assertTrue(grade['pass'])


if __name__ == '__main__':
  unittest.main()
