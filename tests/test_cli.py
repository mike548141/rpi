# End-to-end smoke tests: run the actual CLIs as subprocesses against temp files on the local disk.
# These exercise the real write/read benchmark and verify paths plus the JSON output contracts,
# all hardware-independent (they touch a scratch file, not an SD card). Kept small/fast.
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(argv, timeout=60):
  return subprocess.run([sys.executable] + argv, cwd=ROOT, capture_output=True,
                        text=True, timeout=timeout)


class SdbenchCli(unittest.TestCase):
  def test_json_output_contract(self):
    tmp = tempfile.mkdtemp()
    try:
      proc = run(['sdbench.py', '--json', '--runs', '1', '--size-mb', '2',
                  '--seconds', '1', '--dir', tmp])
      self.assertEqual(proc.returncode, 0, proc.stderr)
      doc = json.loads(proc.stdout)
      # Headline means for all three phases, each carrying a latency distribution (the 0.8 feature)
      for phase in ('seq_write', 'rand_write', 'rand_read'):
        self.assertIn(phase, doc['mean'])
        self.assertIn('lat', doc['mean'][phase])
      self.assertIn('samples', doc)
    finally:
      shutil.rmtree(tmp, ignore_errors=True)


class SdverifyCli(unittest.TestCase):
  def test_partial_sweep_passes_on_genuine_disk(self):
    tmp = tempfile.mkdtemp()
    try:
      # A tiny 4 MB capped sweep of a real, genuine local filesystem must verify clean and exit 0
      proc = run(['sdverify.py', '--json', '--capacity-mb', '4', '--dir', tmp])
      self.assertEqual(proc.returncode, 0, proc.stderr)
      doc = json.loads(proc.stdout)
      self.assertTrue(doc['ok'], doc)
      self.assertIsNone(doc['first_bad_offset'])
    finally:
      shutil.rmtree(tmp, ignore_errors=True)


class SdinfoCli(unittest.TestCase):
  def test_help_runs(self):
    proc = run(['rpi-sdinfo.py', '--help'])
    self.assertEqual(proc.returncode, 0, proc.stderr)
    self.assertIn('usage', proc.stdout.lower())

  def test_db_query_missing_db_is_clean_error(self):
    # --db-query on a path with no database must fail cleanly (exit 2 + a plain message),
    # not throw a traceback.
    tmp = tempfile.mkdtemp()
    dbpath = os.path.join(tmp, 'results.db')
    try:
      proc = run(['rpi-sdinfo.py', '--db-query', dbpath, '--json'])
      self.assertEqual(proc.returncode, 2, proc.stderr)
      self.assertNotIn('Traceback', proc.stderr)
      self.assertIn('database', (proc.stdout + proc.stderr).lower())
    finally:
      shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
  unittest.main()
