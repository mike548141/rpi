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
SRC = os.path.join(ROOT, 'src')

# Invoke the package modules with `python -m`, putting src/ on PYTHONPATH so this works without an
# install. These are the same entry points the console scripts (rpi-sdinfo / rpi-sdbench / rpi-sdverify)
# resolve to, so the smoke test exercises the shipped code paths.
_MODULE = {'sdinfo': 'rpi_sdinfo', 'bench': 'rpi_sdinfo.bench', 'verify': 'rpi_sdinfo.verify'}


def run(tool, args, timeout=60):
  env = dict(os.environ, PYTHONPATH=SRC + os.pathsep + os.environ.get('PYTHONPATH', ''))
  return subprocess.run([sys.executable, '-m', _MODULE[tool]] + args, cwd=ROOT,
                        capture_output=True, text=True, timeout=timeout, env=env)


class SdbenchCli(unittest.TestCase):
  def test_json_output_contract(self):
    tmp = tempfile.mkdtemp()
    try:
      proc = run('bench', ['--json', '--runs', '1', '--size-mb', '2',
                           '--seconds', '1', '--dir', tmp])
      self.assertEqual(proc.returncode, 0, proc.stderr)
      doc = json.loads(proc.stdout)
      # Headline means for all three phases, each carrying a latency distribution (the 0.8 feature)
      for phase in ('seq_write', 'rand_write', 'rand_read'):
        self.assertIn(phase, doc['mean'])
        self.assertIn('lat', doc['mean'][phase])
      self.assertIn('samples', doc)
      self.assertNotIn('block_sweep', doc)  # off by default
    finally:
      shutil.rmtree(tmp, ignore_errors=True)

  def test_block_sweep_curve(self):
    tmp = tempfile.mkdtemp()
    try:
      proc = run('bench', ['--json', '--runs', '1', '--size-mb', '2',
                           '--seconds', '1', '--block-sweep', '--dir', tmp])
      self.assertEqual(proc.returncode, 0, proc.stderr)
      doc = json.loads(proc.stdout)
      sweep = doc['block_sweep']
      # Ascending block sizes, each with a throughput and a latency distribution
      self.assertEqual([e['block_bytes'] for e in sweep], sorted(e['block_bytes'] for e in sweep))
      for entry in sweep:
        self.assertGreaterEqual(entry['mbps'], 0.0)
        self.assertIn('p95_ms', entry['lat'])
    finally:
      shutil.rmtree(tmp, ignore_errors=True)


class SdverifyCli(unittest.TestCase):
  def test_partial_sweep_passes_on_genuine_disk(self):
    tmp = tempfile.mkdtemp()
    try:
      # A tiny 4 MB capped sweep of a real, genuine local filesystem must verify clean and exit 0
      proc = run('verify', ['--json', '--capacity-mb', '4', '--dir', tmp])
      self.assertEqual(proc.returncode, 0, proc.stderr)
      doc = json.loads(proc.stdout)
      self.assertTrue(doc['ok'], doc)
      self.assertIsNone(doc['first_bad_offset'])
    finally:
      shutil.rmtree(tmp, ignore_errors=True)


class SdinfoCli(unittest.TestCase):
  def test_help_runs(self):
    proc = run('sdinfo', ['--help'])
    self.assertEqual(proc.returncode, 0, proc.stderr)
    self.assertIn('usage', proc.stdout.lower())

  def test_block_sweep_in_benchmark_block(self):
    # The combined tool carries the sweep under benchmark.block_sweep when --block-sweep is given.
    # Exit 1 is a legitimate outcome here, not an error: with no card class known, sdinfo grades the
    # medium against the A1 floor (ADR 0004 — honest grading), and a shared CI runner's disk can
    # genuinely dip below A1 under O_DSYNC. This test's contract is the JSON shape, not the speed of
    # whatever disk CI lends us; exit 2 (a real failure) still fails the assertion.
    tmp = tempfile.mkdtemp()
    try:
      proc = run('sdinfo', ['--json', '--runs', '1', '--size-mb', '2',
                            '--seconds', '1', '--block-sweep', '--dir', tmp])
      self.assertIn(proc.returncode, (0, 1), proc.stderr)
      doc = json.loads(proc.stdout)
      self.assertIn('block_sweep', doc['benchmark'])
      self.assertTrue(doc['benchmark']['block_sweep'])
    finally:
      shutil.rmtree(tmp, ignore_errors=True)

  def test_db_query_missing_db_is_clean_error(self):
    # --db-query on a path with no database must fail cleanly (exit 2 + a plain message),
    # not throw a traceback.
    tmp = tempfile.mkdtemp()
    dbpath = os.path.join(tmp, 'results.db')
    try:
      proc = run('sdinfo', ['--db-query', dbpath, '--json'])
      self.assertEqual(proc.returncode, 2, proc.stderr)
      self.assertNotIn('Traceback', proc.stderr)
      self.assertIn('database', (proc.stdout + proc.stderr).lower())
    finally:
      shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
  unittest.main()
