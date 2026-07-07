#!/usr/bin/env python3
# Generate a CycloneDX 1.5 SBOM (Software Bill of Materials) for rpi-sdinfo.
#
# This is DEV/RELEASE tooling, not part of the shipped package - it never imports at runtime and adds no
# runtime dependency (ADR 0001). It is itself stdlib-only, which is the point: rpi-sdinfo has *zero* runtime
# dependencies, so its entire supply chain is the one `rpi-sdinfo` component over the Python standard library.
# The SBOM therefore has an empty `components` list and a root `dependencies` entry that depends on nothing -
# a provably tiny attack surface, machine-readable. See ADR 0005.
#
# Usage:
#   python3 tools/gen_sbom.py                 # write the SBOM to stdout
#   python3 tools/gen_sbom.py -o sbom.cdx.json
#
# The version is read from the package's __version__ (the single source of truth); the stable metadata
# (name, description, licence, repository) is read from pyproject.toml.
import argparse
import datetime
import json
import os
import re
import sys
import uuid

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_version():
  """The single source of truth for the version is __version__ in the package __init__."""
  init_py = os.path.join(_ROOT, 'src', 'rpi_sdinfo', '__init__.py')
  with open(init_py) as fh:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', fh.read(), re.MULTILINE)
  if not match:
    raise SystemExit('could not find __version__ in ' + init_py)
  return match.group(1)


def _read_metadata():
  """Pull the stable project facts from pyproject.toml.

  Uses tomllib when available (Python 3.11+); otherwise falls back to a small targeted parse of the handful
  of scalar fields we need, so the generator still runs on the project's 3.6+ floor without a TOML dependency.
  """
  pyproject = os.path.join(_ROOT, 'pyproject.toml')
  with open(pyproject, 'rb') as fh:
    raw = fh.read()
  try:
    import tomllib
    data = tomllib.loads(raw.decode('utf-8'))
    project = data.get('project', {})
    licence = project.get('license', {})
    return {
      'name': project.get('name', 'rpi-sdinfo'),
      'description': project.get('description', ''),
      'license': licence.get('text', '') if isinstance(licence, dict) else str(licence),
      'repository': project.get('urls', {}).get('Repository', ''),
    }
  except ImportError:
    return _metadata_from_text(raw.decode('utf-8'))


def _metadata_from_text(text):
  """Small targeted parse of pyproject.toml's scalar fields, for Python < 3.11 that lacks tomllib.

  Only the flat `key = "value"` fields we need are read; this is not a general TOML parser.
  """
  def scalar(key):
    m = re.search(r'^%s\s*=\s*"([^"]*)"' % re.escape(key), text, re.MULTILINE)
    return m.group(1) if m else ''

  licence_m = re.search(r'^license\s*=\s*\{\s*text\s*=\s*"([^"]*)"', text, re.MULTILINE)
  return {
    'name': scalar('name') or 'rpi-sdinfo',
    'description': scalar('description'),
    'license': licence_m.group(1) if licence_m else '',
    'repository': scalar('Repository'),
  }


def build_sbom(version, metadata, serial_number=None, timestamp=None):
  """Assemble the CycloneDX 1.5 SBOM document as a dict.

  serial_number / timestamp are injectable so the output is deterministic under test; in normal use they
  default to a fresh UUID and the current UTC time.
  """
  purl = 'pkg:pypi/%s@%s' % (metadata['name'], version)
  serial_number = serial_number or ('urn:uuid:' + str(uuid.uuid4()))
  if timestamp is None:
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

  component = {
    'type': 'application',
    'bom-ref': purl,
    'name': metadata['name'],
    'version': version,
    'purl': purl,
  }
  if metadata.get('description'):
    component['description'] = metadata['description']
  if metadata.get('license'):
    # SPDX id form; Apache-2.0 is a valid SPDX identifier
    component['licenses'] = [{'license': {'id': metadata['license']}}]
  if metadata.get('repository'):
    component['externalReferences'] = [{'type': 'vcs', 'url': metadata['repository']}]

  return {
    'bomFormat': 'CycloneDX',
    'specVersion': '1.5',
    'serialNumber': serial_number,
    'version': 1,
    'metadata': {
      'timestamp': timestamp,
      'tools': [{'vendor': 'rpi-sdinfo', 'name': 'gen_sbom.py', 'version': version}],
      'component': component,
    },
    # Empty by design: zero third-party runtime dependencies (stdlib only). This is the selling point.
    'components': [],
    # The root component depends on nothing.
    'dependencies': [{'ref': purl, 'dependsOn': []}],
  }


def main(argv=None):
  """Generate the SBOM and write it to stdout (or -o file). Returns the process exit code."""
  parser = argparse.ArgumentParser(description='Generate a CycloneDX 1.5 SBOM for rpi-sdinfo (stdlib-only).')
  parser.add_argument('-o', '--output', default=None, help='Write to this file instead of stdout')
  args = parser.parse_args(argv)

  sbom = build_sbom(_read_version(), _read_metadata())
  text = json.dumps(sbom, indent=2) + '\n'
  if args.output:
    with open(args.output, 'w') as fh:
      fh.write(text)
    sys.stderr.write('wrote %s (%d components)\n' % (args.output, len(sbom['components'])))
  else:
    sys.stdout.write(text)
  return 0


if __name__ == '__main__':
  sys.exit(main())
