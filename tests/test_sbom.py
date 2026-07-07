# Tests for the CycloneDX SBOM generator (tools/gen_sbom.py). The generator is dev/release tooling, not part
# of the shipped package, so it is loaded by path rather than as a package import.
import os
import sys
import unittest

from _loader import load_sdinfo

_TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools')
if _TOOLS not in sys.path:
  sys.path.insert(0, _TOOLS)

import gen_sbom  # noqa: E402


class BuildSbom(unittest.TestCase):
  META = {'name': 'rpi-sdinfo', 'description': 'desc', 'license': 'Apache-2.0',
          'repository': 'https://github.com/mike548141/rpi'}

  def _sbom(self):
    return gen_sbom.build_sbom('1.2.3', self.META,
                               serial_number='urn:uuid:fixed', timestamp='2026-01-01T00:00:00Z')

  def test_cyclonedx_envelope(self):
    doc = self._sbom()
    self.assertEqual(doc['bomFormat'], 'CycloneDX')
    self.assertEqual(doc['specVersion'], '1.5')
    self.assertEqual(doc['serialNumber'], 'urn:uuid:fixed')
    self.assertEqual(doc['metadata']['timestamp'], '2026-01-01T00:00:00Z')

  def test_zero_dependencies_is_the_point(self):
    # The whole value of the SBOM here is that the component list is empty and the root depends on nothing
    doc = self._sbom()
    self.assertEqual(doc['components'], [])
    self.assertEqual(len(doc['dependencies']), 1)
    self.assertEqual(doc['dependencies'][0]['dependsOn'], [])
    self.assertEqual(doc['dependencies'][0]['ref'], 'pkg:pypi/rpi-sdinfo@1.2.3')

  def test_component_carries_purl_licence_and_vcs(self):
    comp = self._sbom()['metadata']['component']
    self.assertEqual(comp['type'], 'application')
    self.assertEqual(comp['purl'], 'pkg:pypi/rpi-sdinfo@1.2.3')
    self.assertEqual(comp['licenses'][0]['license']['id'], 'Apache-2.0')
    self.assertEqual(comp['externalReferences'][0], {'type': 'vcs', 'url': self.META['repository']})

  def test_deterministic_when_serial_and_timestamp_injected(self):
    self.assertEqual(gen_sbom.build_sbom('1.2.3', self.META, 'urn:uuid:x', '2026-01-01T00:00:00Z'),
                     gen_sbom.build_sbom('1.2.3', self.META, 'urn:uuid:x', '2026-01-01T00:00:00Z'))


class Metadata(unittest.TestCase):
  def test_version_matches_package(self):
    self.assertEqual(gen_sbom._read_version(), load_sdinfo().VERSION)

  def test_read_metadata_from_pyproject(self):
    meta = gen_sbom._read_metadata()
    self.assertEqual(meta['name'], 'rpi-sdinfo')
    self.assertEqual(meta['license'], 'Apache-2.0')
    self.assertEqual(meta['repository'], 'https://github.com/mike548141/rpi')

  def test_fallback_parser_matches_tomllib_path(self):
    # The <3.11 regex fallback must extract the same scalar facts as the tomllib path
    root = os.path.dirname(_TOOLS)
    with open(os.path.join(root, 'pyproject.toml'), encoding='utf-8') as fh:
      meta = gen_sbom._metadata_from_text(fh.read())
    self.assertEqual(meta['name'], 'rpi-sdinfo')
    self.assertEqual(meta['license'], 'Apache-2.0')
    self.assertEqual(meta['repository'], 'https://github.com/mike548141/rpi')
    self.assertTrue(meta['description'])


if __name__ == '__main__':
  unittest.main()
