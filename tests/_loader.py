# Shared test helper: import the three tool modules from the repo root.
# rpi-sdinfo.py has a hyphen in its name, so it cannot be imported with a plain
# `import`; load it by path via importlib. sdbench / sdverify import normally.
import importlib.util
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
  sys.path.insert(0, _ROOT)


def load_sdinfo():
  path = os.path.join(_ROOT, 'rpi-sdinfo.py')
  spec = importlib.util.spec_from_file_location('rpi_sdinfo', path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def build_csd(structure, tran_speed=0x32, read_bl_len=9, c_size=0, c_size_mult=7, ccc=0x5B5):
  # Independently pack a 128-bit CSD register so decode_csd() can be round-tripped against a
  # register we built from the SD spec's bit layout (not from decode_csd itself).
  value = 0

  def put(field, hi, lo):
    nonlocal value
    mask = (1 << (hi - lo + 1)) - 1
    value |= (field & mask) << lo

  put(structure, 127, 126)
  put(ccc, 95, 84)
  put(tran_speed, 103, 96)
  if structure == 0:                 # v1.0 SDSC
    put(read_bl_len, 83, 80)
    put(c_size, 73, 62)
    put(c_size_mult, 49, 47)
  elif structure == 1:               # v2.0 SDHC/SDXC
    put(c_size, 69, 48)
  elif structure == 2:               # v3.0 SDUC
    put(c_size, 75, 48)
  return '%032x' % value


def csize_for_capacity_v2(capacity_bytes):
  # Inverse of the v2.0/v3.0 capacity formula: capacity = (c_size + 1) * 512 * 1024
  return capacity_bytes // (512 * 1024) - 1
