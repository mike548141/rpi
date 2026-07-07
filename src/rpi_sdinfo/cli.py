#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.8-20260705
# File:         src/rpi_sdinfo/cli.py
# License:      Apache-2.0
# Language:     Python 3.6 or later
# Source:       https://github.com/mike548141/sdinfo/
#
# Description:
#   Performance test SD cards and MMC, and try (perhaps in vain) to help people to spot fake MMC/SD cards by comapring the cards registers to it branding.
#   I'm using gigabyte (GB) for storage and mebibyte (MiB) for memory because thats what I see they industry typically using in product branding and marketing
#
# Platforms:
#   Linux (Raspberry Pi)  - full detail: reads the SD/MMC CID/CSD registers from sysfs to identify make, model
#                           and branding, plus filesystem and IO statistics. Designed on a Raspberry Pi 3 Model B
#                           and a Pi Zero W running Raspberry Pi OS Lite 12 (bookworm).
#   macOS                 - limited: macOS does not expose the SD CID/CSD registers, so identity is whatever the
#                           card reader reports (capacity, media name, bus) via diskutil. The performance test
#                           and grading still work.
#   Windows               - limited: Windows does not expose the SD CID/CSD registers either, so identity is the
#                           drive's capacity, volume label and removable flag. The performance test and grading
#                           still work. Point --dir at the card's drive letter, e.g. --dir E:\
#
# Output:
#   Human-readable by default; --format json emits the whole result as a JSON document on stdout (progress and
#   messages go to stderr) so the tool can be driven by other software and scripts. Exit codes:
#     0  success - card graded PASS, or run with --no-benchmark
#     1  card graded FAIL (slower than its rated / assumed class)
#     2  usage error or unsupported platform
#
# Pre-requisite:
#   Performance testing is now native Python (see bench.py) - no external fio dependency. Nothing to install.
#
# References:
#
# Inputs (parameters):
#
# Outputs:
#

# Known limitations / planned work: see ROADMAP.md
# Remaining assumptions worth calling out inline:
## fio had a faux pas sometime ago where it confused Base-10 and Base-2 (e.g. MB and MiB). So I'm not sure what units we are getting from fio here but I'm assuming Base-10
## Uses the Linux kernel erase_size as the addressable block size; erase_size 0 (a card that is not block-addressed) falls back to 512 and is flagged via cross_check (resolve_block_size)
## f_num() is a workaround for f-strings not combining localisation with a max number of decimal places

#======================================
# Import the libraries
#--------------------------------------

# Command line arguments
import argparse

# Time delta and ISO timestamps for the report
import datetime

# Hash encoding
import hashlib

# Machine-readable (--format json) output
import json

# Locale relevant feedback
import locale

# Floor for the best-half median
import math

# Read files
import os

# Platform info like OS kernel
import platform

# Parse macOS diskutil -plist output
import plistlib

# Regular expression matching
import re

# Advanced math
import statistics

# Optional persist-a-run-to-a-local-database (--save-db)
import sqlite3

# Run external commands (dumpe2fs on Linux, diskutil on macOS)
import subprocess

# For the exit call
import sys

# Benchmark target directory default
import tempfile

# Sibling package modules. Aliased to their historical names so the call sites below read unchanged:
#   bench   - native, dependency-free performance benchmark (replaces fio)
#   verify  - native, dependency-free capacity-fraud sweep (f3/h2testw style)
#   ui      - shared, dependency-free terminal styling (colour, sections, badges, spinner)
from . import bench as sdbench
from . import verify as sdverify
from . import ui

#======================================
# Declare the constants
#--------------------------------------

# Tool version and the version of the JSON document shape emitted by --format json. Bump SCHEMA only on a
# breaking change to the JSON structure so downstream consumers can rely on it
from . import __version__ as VERSION
SCHEMA = 'rpi-sdinfo/1'

# The default Linux device for the MMC or SD card (overridable with --device; the partition defaults to <device>p2)
block_device = 'mmcblk0'

# Where --save-db writes when no path is given: a per-user database that accumulates every run (the local seed of
# the crowd-sourced card database in ROADMAP). Kept out of the working directory so repeated runs pile into one file
default_db = os.path.join(os.path.expanduser('~'), '.rpi-sdinfo', 'results.db')

# The total number of performance tests to run to ensure a consistent result (overridable with --runs)
max_runs = 6
# Name of the file created (and removed) during performance testing
test_file_name = 'sd.test.file'

# Set the locale
locale.setlocale(locale.LC_ALL, '')

# Look up table (dict). The MID and OID are defined, controlled and assigned by the SD-3C, LLC
# They do not publish the list as they consider it to be confidential information, so this is all crowd sourced and really needs better data
manufacturer = {
  'MMC' : {
    '0x000000' : {
      'manufacturer' : 'SanDisk'
    },
    '0x000002' : {
      'manufacturer' : 'Kingston, or SanDisk'
    },
    '0x000003' : {
      'manufacturer' : 'Toshiba'
    },
    '0x000005' : {
      'manufacturer' : 'Unknown'
    },
    '0x000006' : {
      'manufacturer' : 'Unknown'
    },
    '0x000011' : {
      'manufacturer' : 'Toshiba'
    },
    '0x000013' : {
      'manufacturer' : 'Micron'
    },
    '0x000015' : {
      'manufacturer' : 'Samsung, SanDisk, or LG'
    },
    '0x000037' : {
      'manufacturer' : 'KingMax'
    },
    '0x000044' : {
      'manufacturer' : 'ATP'
    },
    '0x000045' : {
      'manufacturer' : 'SanDisk Corporation',
      '0x0100' : {
        'SEM16' : {
          '0x4' : {
            'label' : 'ChromeBook Internal eMMC'            # CID:45010053454d31364790e03506aebf4d
          }
        }
      }
    },
    '0x000070' : {
      'manufacturer' : 'Kingston'
    },
    '0x00002c' : {
      'manufacturer' : 'Kingston'
    },
    '0x0000fe' : {
      'manufacturer' : 'Micron'
    }
  },
  'SD' : {
    '0x000001' : {
      'manufacturer' : 'Panasonic',
      '0x5041' : {
        'oem' : 'Panasonic'
      }
    },
    '0x000002' : {
      'manufacturer' : 'Kingston, Toshiba, or Viking',
      '0x544d' : {
        'oem' : 'Kingston, Toshiba, or Viking',
        'SA64G' : {
          '0x5' : {
            'label' : 'Kingston 64 GB microSDXC U1 C10',    # CID:02544d534136344753292e67a2013343
            'speed_class' : ['U1', 'C10']
          }
        },
        'SD02G' : {
          '0x2' : {
            'label' : 'Kingston 2 GB SDSC'                  # CID:02544d534430324728ad78243300793d
          }
        }
      }
    },
    '0x000003' : {
      'manufacturer' : 'SanDisk',
      '0x5054' : {
        'oem' : 'SanDisk'
      },
      '0x5344' : {
        'oem' : 'SanDisk',
        'SD02G' : {
          '0x8' : {
            'label' : 'SanDisk Blue 2 GB SDSC'              # CID:035344534430324780019acc7600844b
          }
        },
        'SU01G' : {
          '0x8' : {
            'label' : 'SanDisk Ultra II 1 GB microSDSC'     # CID:035344535530314780401c751300637d
          }
        },
        'SU32G' : {
          '0x8' : {
            'label' : 'SanDisk 32 GB microSDHC C4',         # CID:035344535533324780718848c800b7fb
            'speed_class' : ['C4']
          }
        },
        'SU64G' : {
          '0x8' : {
            'label' : 'SanDisk Ultra 64 GB microSDXC U1',   # CID:0353445355363447801013d98600d6d3
            'speed_class' : ['U1']
          }
        }
      }
    },
    '0x000008' : {
      'manufacturer' : 'Silicon Power'
    },
    '0x000012' : {
      '0x3456' : {
        'MS' : {
          '0x1' : {
            'label' : 'Unbranded 2 GB microSDSC'            # CID:1234564d532020201000004c6300c853
          }
        }
      },
      '0x5678' : {
        'ASTC' : {
          '0x3' : {
            'label' : 'Strontium 16 GB microSDHC C10',      # CID:1256784153544300340000059b01032f
            'speed_class' : ['C10']
          }
        }
      }
    },
    '0x000018' : {
      'manufacturer' : 'Infineon'
    },
    '0x000027' : {
      'manufacturer' : 'Phison Electronics Corporation',
      '0x5048' : {
        'oem' : 'AgfaPhoto, Delkin, Integral, Lexar, Patriot, PNY, Polaroid, Sony, or Verbatim',
        'SD32G' : {
          '0x3' : {
            'label' : 'Patriot 32 GB SDHC C10',             # CID:275048534433324730b018bd6700abe5
            'speed_class' : ['C10']
          }
        }
      }
    },
    '0x000028' : {
      'manufacturer' : 'Lexar',
      '0x4245' : {
        'oem' : 'Lexar, PNY, or ProGrade'
      }
    },
    '0x000030' : {
      'manufacturer' : 'SanDisk'
    },
    '0x000031' : {
      'manufacturer' : 'Silicon Power',
      '0x5350' : {
        'oem' : 'Silicon Power'
      }
    },
    '0x000033' : {
      'manufacturer' : 'STMicroelectronics'
    },
    '0x000041' : {
      'manufacturer' : 'Kingston',
      '0x3432' : {
        'oem' : 'Kingston',
        'SD128' : {
          '0x3' : {
            'label' : 'Kingston 128 GB SDXC C10',           # CID:41343253443132383002b800b600da6f
            'speed_class' : ['C10']
          }
        }
      }
    },
    '0x00006f' : {
      'manufacturer' : 'STMicroelectronics'
    },
    '0x000074' : {
      'manufacturer' : 'Transcend',
      '0x4a45' : {
        'oem' : 'Transcend'
      },
      '0x4a60' : {
        'oem' : 'Transcend'
      }
    },
    '0x000076' : {
      'manufacturer' : 'Patriot'
    },
    '0x000082' : {
      'manufacturer' : 'Gobe, or Sony',
      '0x4a54' : {
        'oem' : 'Gobe, or Sony'
      }
    },
    '0x000088' : {
      '0x0302' : {
        '1232' : {
          '0x1' : {
            'label' : 'Pretec 2 GB microSDSC'               # CID:8803023132333220100000cea40071b9
          }
        }
      }
    },
    '0x000089' : {
      'manufacturer' : 'Unknown',
      '0x0303' : {
        'NCard' : {
          '0x0' : {
            'label' : 'Team 32 GB C10',                     # CID:8903034e43617264000000667000b285
            'speed_class' : ['C10']
          }
        }
      }
    },
    '0x00001b' : {
      'manufacturer' : 'Samsung, or Transcend',
      '0x534d' : {
        'oem' : 'Samsung, or ProGrade',
        '00000' : {
          '0x1' : {
            'alternate' : 'Raspberry Pi BMC SDHC',          # CID:1b534d3030303030100337410200d13b
            'label' : 'Samsung 32 GB SDHC C10',             # CID:1b534d3030303030107d11463800c199
            'speed_class' : ['C10']
          }
        }
      }
    },
    '0x00001c' : {
      'manufacturer' : 'Transcend'
    },
    '0x00001d' : {
      'manufacturer' : 'AData, or Corsair',
      '0x4144' : {
        'oem' : 'AData'
      }
    },
    '0x00001e' : {
      'manufacturer' : 'Transcend'
    },
    '0x00001f' : {
      'manufacturer' : 'Kingston'
    },
    '0x00009c' : {
      '0x534f' : {
        'oem' : 'Angelbird (V60), or Hoodman'
      },
      '0x4245' : {
        'oem' : 'Angelbird (V90)'
      }
    }
  }
}

# Expected performance classes defined by SD-3C
# https://www.sdcard.org/developers/sd-standard-overview/application-performance-class/
speed_class = {
  'C2' : {
    'seq_write' : 2
  },
  'C4' : {
    'seq_write' : 4
  },
  'C6' : {
    'seq_write' : 6
  },
  'C10' : {
    'seq_write' : 10
  },
  'U1' : {
    'seq_write' : 10
  },
  'U3' : {
    'seq_write' : 30
  },
  'V6' : {
    'seq_write' : 6
  },
  'V10' : {
    'seq_write' : 10
  },
  'V30' : {
    'seq_write' : 30
  },
  'V60' : {
    'seq_write' : 60
  },
  'V90' : {
    'seq_write' : 90
  },
  'E150' : {
    'seq_write' : 150
  },
  'E300' : {
    'seq_write' : 300
  },
  'E450' : {
    'seq_write' : 450
  },
  'E600' : {
    'seq_write' : 600
  },
  'A1' : {
    'rand_read' : 1500,
    'rand_write' : 500,
    'seq_write' : 10
  },
  'A2' : {
    'rand_read' : 4000,
    'rand_write' : 2000,
    'seq_write' : 10
  },
  'bus' : {
    'default' : {
      'version' : 1.01,
      'seq_write' : 12.5
    },
    'high' : {
      'version' : 1.10,
      'seq_write' : 25
    },
    'UHS-I' : {
      'version' : 3.01,
      'sdr50' : {
        'seq_write' : 50
      },
      'sdr104' : {
        'seq_write' : 104
      }
    },
    'UHS-II' : {
      'version' : 4.00,
      'seq_write' : 156
    },
    'UHS-III' : {
      'version' : 6.00,
      'seq_write' : 312
    },
    'sd_express' : {
      '7.00' : {
        'seq_write' : 985
      },
      '7.10' : {
        'seq_write' : 985
      },
      '8.00' : {
        'seq_write' : 1970          # Can also be up to 3,940 MBps using PCIe Gen.4 x 2 Lane
      },
      '9.10' : {
        'seq_write' : 1970
      }
    }
  }
}

#======================================
# Declare the functions
#--------------------------------------

# Workaround for f strings to handle locale, rounding, and variable type in one
def f_num(num_value, dec_places=0):
  """Format a number with the active locale's thousands grouping, rounded to dec_places."""
  if isinstance(num_value, str):
    num_value = float(num_value)
  num_value = round(num_value, dec_places)
  return f"{num_value:n}"

def read_file(file_path, search_for='', return_scope='all', replace_with=''):
  """Returns '' (not None) when the file is absent so callers can safely concatenate, e.g. a Pi Zero has no eth0.
  Also returns '' (rather than a traceback) when a node exists but cannot be read - e.g. a permission-gated
  sysfs/debugfs path such as the Bluetooth identity, which needs root.
  """
  if os.path.isfile(file_path):
    file_contents = ''
    try:
      with open(file_path, 'r') as file_pointer:
        if return_scope == 'all':
          # Return everything in the file
          file_contents = file_pointer.read().replace(search_for, replace_with)
        elif return_scope == 'lines':
          # Return just the line indicated by its number
          file_contents = file_pointer.readlines()[search_for]
        elif return_scope == 'regex':
          # Return all lines that contains the regexp specified
          for file_line in file_pointer:
            if re.search(search_for, file_line):
              file_contents += file_line
    except OSError:
      return ''
    return file_contents
  return ''

def parse_kv(lines, separator=':'):
  """Parse 'key: value' style output (dumpe2fs, /proc/meminfo, ...) into a dict keyed by the label so we look
  attributes up by name rather than by fragile line number / character offset
  """
  result = {}
  for line in lines:
    if separator in line:
      key, _, value = line.partition(separator)
      result[key.strip()] = value.strip()
  return result

def mib(mem_value):
  """Convert a /proc/meminfo style 'N kB' value to MiB (its numeric leading field / 1024)"""
  return int(mem_value.split()[0]) / 1024

def safe_div(numerator, denominator):
  """Guard the disk-throughput maths against a divide-by-zero on a card that has been idle since boot"""
  return numerator / denominator if denominator else 0

def resolve_block_size(erase_size):
  """The kernel exposes a card's addressable block size as erase_size: 512 for a normal block-addressed
  card, 0 for a card that is not block-addressed. Fall back to 512 in the 0 case but report that we
  assumed it, so the capacity figure derived from it can be flagged rather than silently trusted.
  Returns (block_size, assumed).
  """
  try:
    erase_size = int(erase_size)
  except (TypeError, ValueError):
    erase_size = 0
  if erase_size > 0:
    return erase_size, False
  return 512, True

def _lookup(tree, *keys, default=None):
  """Walk a nested dict by successive keys, returning default the moment a level is missing or is not a
  dict. Replaces a broad try/except KeyError around the CID database lookups: that also swallowed
  unrelated KeyErrors and turned a non-dict intermediate node into an uncaught TypeError traceback.
  """
  node = tree
  for key in keys:
    if not isinstance(node, dict) or key not in node:
      return default
    node = node[key]
  return node

def best_median(values, higher_is_better=True):
  """Real world runs are noisy, so drop the worst half (slow outliers, or high-latency outliers) and take the
  median of what remains as a fair best-guess of the storage's rated performance
  """
  ordered = sorted(values)
  half = math.floor(len(ordered) / 2)
  if higher_is_better:
    return statistics.median(ordered[half:])
  return statistics.median(ordered[:half] or ordered)

#======================================
# CSD register decode + CID/CSD cross-checks (fake detection from metadata alone)
#--------------------------------------
#
# The capacity sweep (verify.py) proves a card's real size by writing to it. This does the complementary,
# instant, non-destructive check: decode what the card *claims* about itself in the CSD register and flag
# internal contradictions. The strongest tell is a Standard-Capacity (v1.0) CSD that claims a High/eXtended
# capacity - physically impossible per the SD spec, so a dead giveaway that a small card's firmware was
# reflashed to lie about its size.

def _bits(value, hi, lo):
  """Extract CSD bits [hi:lo] inclusive from the 128-bit register value (bit 127 is the MSB)"""
  return (value >> lo) & ((1 << (hi - lo + 1)) - 1)

# TRAN_SPEED time-value mantissa table (index -> multiplier), from the SD Physical Layer spec
_TRAN_SPEED_VALUE = [0, 1.0, 1.2, 1.3, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0]
_TRAN_SPEED_UNIT = [0.1, 1.0, 10.0, 100.0]  # Mbit/s per unit code (0..3)

# Minimum sustained sequential write (MB/s) each rated class guarantees. Used not to fail a card, but to explain
# on a *genuine* card why the current bus can't deliver the label - UHS speed is negotiated out-of-band from the
# CSD's TRAN_SPEED field, so a real U3/V30 card is bus-limited on a non-UHS host and would otherwise look slow
# for no visible reason. See SD_CARDS.md for the class tables.
_CLASS_WRITE_MBPS = {
  'C2': 2, 'C4': 4, 'C6': 6, 'C10': 10,
  'U1': 10, 'U3': 30,
  'V6': 6, 'V10': 10, 'V30': 30, 'V60': 60, 'V90': 90,
  'A1': 10, 'A2': 10,
}

def _rated_write_floor(speed_class):
  """Highest sustained-write floor (MB/s) implied by the card's rated-class tokens, or 0 if none are recognised"""
  return max((_CLASS_WRITE_MBPS.get(str(c).upper(), 0) for c in (speed_class or [])), default=0)

def decode_csd(csd_hex):
  """Decode the 128-bit CSD register (a 32-char hex string from sysfs) into the fields we cross-check against
  the branding. Returns None if the register is absent or malformed. Capacity maths follows the SD spec:
  v1.0 (SDSC) uses C_SIZE/C_SIZE_MULT/READ_BL_LEN; v2.0 (SDHC/SDXC) and v3.0 (SDUC) use the 512 KB C_SIZE form
  """
  text = (csd_hex or '').strip().replace(':', '').replace(' ', '')
  if len(text) != 32:
    return None
  try:
    value = int(text, 16)
  except ValueError:
    return None

  structure = _bits(value, 127, 126)
  tran_speed = _bits(value, 103, 96)
  speed = _TRAN_SPEED_UNIT[tran_speed & 0x7] * _TRAN_SPEED_VALUE[(tran_speed >> 3) & 0xF]
  result = {
    'structure': structure,
    'ccc': _bits(value, 95, 84),                       # Card Command Classes bitmap
    'tran_speed_mbit': round(speed, 1),
    'read_bl_len': None,
    'capacity_bytes': None,
    'capacity_type': 'unknown',
  }

  if structure == 0:                                    # CSD v1.0 - Standard Capacity
    read_bl_len = _bits(value, 83, 80)
    c_size = _bits(value, 73, 62)
    c_size_mult = _bits(value, 49, 47)
    result['read_bl_len'] = read_bl_len
    result['capacity_bytes'] = (c_size + 1) * (1 << (c_size_mult + 2)) * (1 << read_bl_len)
    result['capacity_type'] = 'SDSC'
  elif structure == 1:                                  # CSD v2.0 - High / eXtended Capacity
    c_size = _bits(value, 69, 48)
    result['read_bl_len'] = 9
    result['capacity_bytes'] = (c_size + 1) * 512 * 1024
    result['capacity_type'] = 'SDXC' if result['capacity_bytes'] > 32 * 1000 ** 3 else 'SDHC'
  elif structure == 2:                                  # CSD v3.0 - Ultra Capacity
    c_size = _bits(value, 75, 48)
    result['read_bl_len'] = 9
    result['capacity_bytes'] = (c_size + 1) * 512 * 1024
    result['capacity_type'] = 'SDUC'
  return result

def _parse_mdt(mdt):
  """The kernel exposes the CID manufacturing date as 'MM/YYYY'. Return (year, month) or None if unparseable"""
  try:
    month, year = mdt.strip().split('/')
    return int(year), int(month)
  except (ValueError, AttributeError):
    return None

def cross_check(storage, now=None):
  """Compare the card's self-declared facts (CSD capacity/structure, reported capacity, CID date, branding) for
  internal contradictions. Returns a list of findings, each {severity: fail|warn|info, message: str}. 'fail'
  means physically impossible per the spec (a strong counterfeit signal); 'warn'/'info' are softer hints
  """
  findings = []
  decoded = storage.get('csd_decoded')
  reported = storage.get('bytes') or 0

  # Structural validity of the register itself. A genuine SD controller emits a spec-valid CSD; a reflashed or
  # no-name fake often carries garbage in these fields. Note: we deliberately do NOT infer the rated speed class
  # from TRAN_SPEED - UHS bus speed is negotiated out-of-band (CMD6/CMD11), so a genuine UHS card legitimately
  # still reports 25/50 Mbit/s here, and a capability check would false-positive real cards.
  if decoded:
    if decoded.get('structure') == 3:
      findings.append({'severity': 'warn', 'message': 'CSD structure version is reserved (3) - not a valid SD CSD; a malformed register is a counterfeit tell'})
    if not decoded.get('tran_speed_mbit'):
      findings.append({'severity': 'warn', 'message': 'CSD TRAN_SPEED is zero/undefined - a malformed transfer-rate field, not a value a genuine card emits'})
    ccc = decoded.get('ccc') or 0
    missing = [c for c in (0, 2, 4) if not (ccc >> c) & 1]
    if not ccc:
      findings.append({'severity': 'warn', 'message': 'CSD command-classes field is empty (0) - a genuine card always advertises its basic/read/write classes'})
    elif missing:
      findings.append({'severity': 'warn', 'message': 'CSD is missing mandatory command class(es) %s (basic/read/write) - malformed register' % ', '.join(map(str, missing))})
    if decoded.get('structure') == 0 and decoded.get('read_bl_len') not in (9, 10, 11):
      findings.append({'severity': 'warn', 'message': 'CSD READ_BL_LEN %s is outside the legal 9/10/11 - malformed register' % decoded.get('read_bl_len')})

    # NOT a fake signal: a genuine high-class card whose CSD advertises only a default/high-speed bus. UHS speed
    # is negotiated out-of-band (CMD6/CMD11) and simply is not reflected in TRAN_SPEED. We surface it as info so a
    # real card that measures below its label is explained, not silently believed fast or wrongly assumed broken
    if decoded.get('tran_speed_mbit'):
      rated = _rated_write_floor(storage.get('speed_class'))
      ceiling = decoded['tran_speed_mbit'] / 2.0          # 4-bit SD bus: MB/s ~= clock(MHz) x 4 lines / 8 bits
      if rated and rated > ceiling:
        mode = 'default-speed' if decoded['tran_speed_mbit'] <= 25 else 'high-speed'
        findings.append({'severity': 'info', 'message':
          'card is rated for ~%g MB/s but its CSD advertises only a %s bus (~%g MB/s). This is not a fault: UHS '
          'speed is negotiated separately and is not shown in the CSD, so a genuine card reaches its rated speed '
          'only on a UHS-capable host, reader and slot - over a slower interface it is bus-limited to ~%g MB/s'
          % (rated, mode, ceiling, ceiling)})

  if decoded and decoded.get('capacity_bytes'):
    csd_bytes = decoded['capacity_bytes']
    # A Standard-Capacity CSD physically cannot describe more than 2 GB (4 GB with maxed fields). Claiming more
    # is impossible - the classic reflashed-fake signature
    if decoded['structure'] == 0 and reported > 4 * 1000 ** 3:
      findings.append({'severity': 'fail', 'message': 'CSD is Standard-Capacity (v1.0) but the card claims %s GB - impossible per the SD spec; likely a reflashed fake' % f_num(reported / 1000 ** 3, 1)})
    elif decoded['structure'] == 0 and reported > 2 * 1000 ** 3:
      findings.append({'severity': 'warn', 'message': 'CSD is Standard-Capacity (v1.0) but the card claims over 2 GB (SDSC ceiling)'})
    # The CSD's own capacity should match the block-count capacity the kernel reports; a big gap is suspicious
    if reported and abs(csd_bytes - reported) > max(csd_bytes, reported) * 0.03:
      findings.append({'severity': 'warn', 'message': 'CSD capacity %s disagrees with the reported %s' % (f_num(csd_bytes / 1000 ** 3, 1) + ' GB', f_num(reported / 1000 ** 3, 1) + ' GB')})

  mdt = _parse_mdt(storage.get('cid_mdt', ''))
  if mdt and now:
    if (mdt[0], mdt[1]) > (now[0], now[1]):
      findings.append({'severity': 'warn', 'message': 'CID manufacturing date %02d/%04d is in the future - a common counterfeit tell' % (mdt[1], mdt[0])})

  # Branded product name but no manufacturer match usually just means the crowd-sourced DB is incomplete, not
  # a fake - surface it as information so a gap in the table is visible, not alarming
  if storage.get('cid_pnm') and storage.get('manufacturer') in (None, '', 'unknown'):
    findings.append({'severity': 'info', 'message': "product '%s' is not in the CID database yet (unverified make)" % storage['cid_pnm']})

  # The kernel reported erase_size as 0 (card not block-addressed): the capacity above rests on an assumed
  # 512-byte block, so make that assumption visible rather than presenting the figure as measured fact
  if storage.get('block_size_assumed'):
    findings.append({'severity': 'info', 'message': 'card is not block-addressed (erase_size 0); capacity assumes a 512-byte block'})

  return findings

def compute_consistency(sys_info):
  """Decode the CSD (if present) and run the cross-checks, stashing both on sys_info. No-op on platforms that
  cannot read the register (macOS/Windows), so it is safe to call unconditionally
  """
  storage = sys_info.get('storage', {})
  storage['csd_decoded'] = decode_csd(storage.get('csd', ''))
  today = datetime.date.today()
  findings = cross_check(storage, now=(today.year, today.month))
  sys_info['consistency'] = {
    'findings': findings,
    'ok': not any(f['severity'] == 'fail' for f in findings),
  }
  return sys_info['consistency']

#======================================
# Gather - Linux (Raspberry Pi)
#--------------------------------------

def gather_linux(args):
  """Read everything the Linux kernel exposes about the Pi and its SD/MMC card, then derive the friendly fields.
  sysfs paths are Linux-only; on any other platform gather_macos() is used instead.
  """
  device = args.device or block_device
  partition = args.partition or (device + 'p2')

  # Load the source files once, up front, so the data is internally consistent and not read twice. Keep the raw
  # text of each source so --raw can dump it verbatim for debugging (parsing bugs, unexpected label spellings)
  dumpe2fs_raw = subprocess.run(['/sbin/dumpe2fs', '-h', '/dev/' + partition], capture_output=True, encoding='utf-8', text=True, timeout=5).stdout
  loadavg_raw = read_file('/proc/loadavg')
  meminfo_raw = read_file('/proc/meminfo')
  diskstats_raw = read_file('/proc/diskstats', ' ' + device + ' ', 'regex')
  fs_info = parse_kv(dumpe2fs_raw.split('\n'))
  load_avg = loadavg_raw.split()
  mem_info = parse_kv(meminfo_raw.split('\n'))
  disk_stats = diskstats_raw.split()
  # Fixed application salt so the anonymised device uuid is stable across runs (a random salt would make it useless as a shared-database identifier). See ROADMAP for a stronger scheme
  salt = b'rpi-sdinfo/device-uuid/v1'
  serial = read_file('/sys/firmware/devicetree/base/serial-number', '\x00')

  sys_info = {
    'platform' : 'linux',
    'device' : device,
    'partition' : partition,
    'hardware' : {
      'model' : read_file('/sys/firmware/devicetree/base/model', '\x00') or 'unknown',
      'serial_number' : serial,
      'uuid' : hashlib.pbkdf2_hmac('sha256', serial.encode('utf-8'), salt, 1000).hex() if serial else '',
      'mac_eth0' : read_file('/sys/class/net/eth0/address', '\n') or 'n/a',
      'mac_wlan0' : read_file('/sys/class/net/wlan0/address', '\n') or 'n/a',
      'mac_bt0' : read_file('/sys/kernel/debug/bluetooth/hci0/identity')[0:17] or 'n/a'
    },
    'software' : {
      'os_release' : platform.freedesktop_os_release().get('PRETTY_NAME', 'Linux') if hasattr(platform, 'freedesktop_os_release') else 'Linux',
      'os_kernel' : platform.release()
    },
    'storage' : {
      'type' : read_file('/sys/block/' + device + '/device/type', '\n'),
      'read_only' : read_file('/sys/block/' + device + '/ro', '\n'),                   # Hardware boolean to force read only, on SD cards thats controlled by a switch on its side
      'force_read_only' : read_file('/sys/block/' + device + '/force_ro', '\n'),       # Software boolean to force read only
      'removable' : read_file('/sys/block/' + device + '/removable', '\n'),
      'blocks' : int(read_file('/sys/block/' + device + '/size', '\n') or 0),
      'block_size' : int(read_file('/sys/block/' + device + '/device/erase_size', '\n') or 0),
      'ocr' : read_file('/sys/block/' + device + '/device/ocr', '\n'),                 # Operation Conditions Register
      'cid' : read_file('/sys/block/' + device + '/device/cid', '\n'),                 # Card Identification register, 16 bytes uniquely identifying the card
      'cid_mid' : read_file('/sys/block/' + device + '/device/manfid', '\n'),          # Manufacturer ID (from CID). 8-bit, assigned by SD-3C
      'cid_oid' : read_file('/sys/block/' + device + '/device/oemid', '\n'),           # OEM/Application ID (from CID). 2-char ASCII, assigned by SD-3C
      'cid_pnm' : read_file('/sys/block/' + device + '/device/name', '\n'),            # Product Name (from CID). 5-char ASCII
      'cid_prv_hw' : read_file('/sys/block/' + device + '/device/hwrev', '\n'),        # Hardware/Product Revision (from CID)
      'cid_prv_fw' : read_file('/sys/block/' + device + '/device/fwrev', '\n'),        # Firmware/Product Revision (from CID)
      'cid_psn' : read_file('/sys/block/' + device + '/device/serial', '\n'),          # Product serial number, 32-bit
      'cid_mdt' : read_file('/sys/block/' + device + '/device/date', '\n'),            # Manufacturing Date (from CID), YYM offset from 2000
      'csd' : read_file('/sys/block/' + device + '/device/csd', '\n'),                 # Card Specific Data register
      'rca' : read_file('/sys/block/' + device + '/device/rca', '\n'),                 # Relative Card Address register
      'dsr' : read_file('/sys/block/' + device + '/device/dsr', '\n'),                 # Driver Stage Register
      'scr' : read_file('/sys/block/' + device + '/device/scr', '\n'),                 # SD Card Configuration Register (SD only)
      'ssr' : read_file('/sys/block/' + device + '/device/ssr', '\n')                  # SD Status Register
    },
    'filesystem' : {
      'state' : fs_info.get('Filesystem state', 'unknown'),
      'created' : fs_info.get('Filesystem created', 'unknown'),
      'last_checked' : fs_info.get('Last checked', 'unknown'),
      'mount_count' : int(fs_info.get('Mount count', 0)),
      'last_mount' : fs_info.get('Last mount time', 'unknown')
    },
    'stats' : {
      'cpu' : {
        'load_1m' : float(load_avg[0]) if load_avg else 0.0,
        'load_5m' : float(load_avg[1]) if len(load_avg) > 1 else 0.0,
        'load_15m' : float(load_avg[2]) if len(load_avg) > 2 else 0.0,
        'threads' : load_avg[3] if len(load_avg) > 3 else 'n/a'
      },
      'memory' : {
        'total' : mib(mem_info.get('MemTotal', '0')),
        'free' : mib(mem_info.get('MemFree', '0')),
        'available' : mib(mem_info.get('MemAvailable', '0')),
        'swap_total' : mib(mem_info.get('SwapTotal', '0')),
        'swap_free' : mib(mem_info.get('SwapFree', '0'))
      },
      'disk' : {
        'read_completed' : int(disk_stats[3]) if len(disk_stats) > 13 else 0,
        'read_sectors' : int(disk_stats[5]) if len(disk_stats) > 13 else 0,
        'read_time' : int(disk_stats[6]) if len(disk_stats) > 13 else 0,
        'write_completed' : int(disk_stats[7]) if len(disk_stats) > 13 else 0,
        'write_sectors' : int(disk_stats[9]) if len(disk_stats) > 13 else 0,
        'write_time' : int(disk_stats[10]) if len(disk_stats) > 13 else 0
      }
    }
  }

  # Analyse - capacity. erase_size is the card's addressable block size (512 when block-addressed);
  # a 0 means the card is not block-addressed, so we assume 512 and flag it (see cross_check / ROADMAP)
  block_size, block_size_assumed = resolve_block_size(sys_info['storage']['block_size'])
  sys_info['storage']['block_size'] = block_size
  sys_info['storage']['block_size_assumed'] = block_size_assumed
  sys_info['storage']['bytes'] = sys_info['storage']['blocks'] * block_size
  sys_info['storage']['GB'] = sys_info['storage']['bytes'] / 1000000000
  sys_info['storage']['GiB'] = sys_info['storage']['bytes'] / 1024 / 1024 / 1024

  # Analyse - look up make, brand, model and rated speed class from the crowd-sourced CID database.
  # _lookup walks the nested table safely (a missing or non-dict node yields the default, not a traceback)
  card_type, mid, oid, pnm, hwrev = (sys_info['storage'][k] for k in ('type', 'cid_mid', 'cid_oid', 'cid_pnm', 'cid_prv_hw'))
  mfr = _lookup(manufacturer, card_type, mid, 'manufacturer', default='unknown')
  sys_info['storage']['manufacturer'] = mfr
  sys_info['storage']['oem'] = _lookup(manufacturer, card_type, mid, oid, 'oem', default=mfr)
  oem = sys_info['storage']['oem']
  sys_info['storage']['label'] = _lookup(manufacturer, card_type, mid, oid, pnm, hwrev, 'label', default=oem)
  sys_info['storage']['speed_class'] = _lookup(manufacturer, card_type, mid, oid, pnm, hwrev, 'speed_class', default=[])

  # Analyse - card read/write and removable state
  read_only, force_ro = sys_info['storage']['read_only'], sys_info['storage']['force_read_only']
  if read_only == '1' and force_ro == '1':
    sys_info['storage']['state'] = 'read only (hardware+software)'
  elif read_only == '1':
    sys_info['storage']['state'] = 'read only (hardware)'
  elif force_ro == '1':
    sys_info['storage']['state'] = 'read only (software)'
  else:
    sys_info['storage']['state'] = 'read/write'
  sys_info['storage']['removable_label'] = 'removable' if sys_info['storage']['removable'] == '1' else 'not removable'

  # Analyse - flag a recent history of high CPU load that could skew the performance test (rendered as a warning
  # by the reporter; kept here as a plain boolean so the JSON output stays clean)
  cpu = sys_info['stats']['cpu']
  cpu['load_high'] = cpu['load_1m'] >= 1.0 or (cpu['load_1m'] >= 0.5 and cpu['load_5m'] >= 0.7 and cpu['load_15m'] >= 0.7)

  # Analyse - real world throughput and IOPS from the kernel's lifetime disk counters (safe_div guards an idle card)
  disk = sys_info['stats']['disk']
  disk['read_avg_mbps'] = safe_div(disk['read_sectors'] * block_size / 1000000, disk['read_time'] / 1000)
  disk['read_avg_iops'] = safe_div(disk['read_completed'], disk['read_time'] / 1000)
  disk['write_avg_mbps'] = safe_div(disk['write_sectors'] * block_size / 1000000, disk['write_time'] / 1000)
  disk['write_avg_iops'] = safe_div(disk['write_completed'], disk['write_time'] / 1000)

  # --raw: keep the unparsed sources so a debugging run can show exactly what the kernel reported, warts and all
  if args.raw:
    sys_info['raw'] = {
      'dumpe2fs': dumpe2fs_raw,
      'proc_loadavg': loadavg_raw,
      'proc_meminfo': meminfo_raw,
      'proc_diskstats': diskstats_raw,
    }
  return sys_info

#======================================
# Gather - macOS
#--------------------------------------

def diskutil_info(path):
  """Return diskutil's info for a path or device as a dict, or {} on any failure. Accepts a mount path (e.g.
  /Volumes/CARD) or a device id (e.g. disk4); macOS resolves either to the underlying whole disk
  """
  try:
    output = subprocess.run(['diskutil', 'info', '-plist', path], capture_output=True, timeout=10).stdout
    return plistlib.loads(output)
  except (subprocess.SubprocessError, OSError, plistlib.InvalidFileException, ValueError):
    return {}

def _device_for_path(path):
  """Resolve the device that backs a directory path via df (diskutil info only accepts a mount point or device)"""
  try:
    lines = subprocess.run(['df', path], capture_output=True, encoding='utf-8', timeout=5).stdout.splitlines()
    return lines[1].split()[0] if len(lines) > 1 else ''
  except (subprocess.SubprocessError, OSError, IndexError):
    return ''

def _diskutil_disk_partitions():
  """diskutil's whole-disks-with-partitions list (each entry has 'DeviceIdentifier' and 'Partitions'/'APFSVolumes'
  carrying per-volume 'MountPoint'). [] on any failure
  """
  try:
    output = subprocess.run(['diskutil', 'list', '-plist'], capture_output=True, timeout=10).stdout
    return plistlib.loads(output).get('AllDisksAndPartitions', [])
  except (subprocess.SubprocessError, OSError, plistlib.InvalidFileException, ValueError):
    return []

def _entry_mountpoint(entry):
  """First mounted volume on a whole-disk entry (a plain partition or an APFS volume), or '' if nothing is mounted"""
  for vol in list(entry.get('Partitions', [])) + list(entry.get('APFSVolumes', [])):
    if vol.get('MountPoint'):
      return vol['MountPoint']
  return ''

def _autodetect_macos_target():
  """With no --device/--dir given, find an inserted removable/external card rather than silently profiling the boot
  disk. Prefer an SD-bus disk over a generic external one (so a card reader wins over, say, a backup drive).
  Returns (device, mountpoint); ('', '') when nothing removable is present
  """
  best = None
  for entry in _diskutil_disk_partitions():
    disk = entry.get('DeviceIdentifier', '')
    if not disk:
      continue
    info = diskutil_info(disk)
    if not info.get('RemovableMediaOrExternalDevice'):
      continue
    bus = info.get('BusProtocol', '')
    score = 2 if ('Secure Digital' in bus or bus == 'SD') else 1
    if best is None or score > best[0]:
      best = (score, disk, _entry_mountpoint(entry))
  return (best[1], best[2]) if best else ('', '')

def _sp_card_reader():
  """system_profiler's built-in-SD-slot tree; [] on any failure or when the Mac has no native reader / no card"""
  try:
    output = subprocess.run(['system_profiler', '-json', 'SPCardReaderDataType'],
                            capture_output=True, encoding='utf-8', timeout=15).stdout
    return json.loads(output).get('SPCardReaderDataType', [])
  except (subprocess.SubprocessError, OSError, ValueError, AttributeError):
    return []

def _find_card_node(tree, device):
  """Depth-first search for the inserted-card entry whose 'bsd_name' matches the whole-disk device (e.g. 'disk4');
  the SD slot nests the card under the reader's '_items'. Returns the node dict, or {} if absent
  """
  stack = list(tree) if isinstance(tree, list) else [tree]
  while stack:
    node = stack.pop()
    if not isinstance(node, dict):
      continue
    if node.get('bsd_name') == device:
      return node
    stack.extend(node.get('_items', []))
  return {}

def macos_card_identity(device, tree=None):
  """Best-effort *real* card identity from the built-in reader, which (unlike diskutil) can surface the card's own
  product/manufacturer/serial rather than just the reader's model. Returns {product, manufacturer, serial} with
  only the keys the profiler actually exposed. USB card readers present as generic mass storage and do not
  appear here, so this mainly enriches Macs with a native SD slot. `tree` is injectable for testing
  """
  node = _find_card_node(_sp_card_reader() if tree is None else tree, device)
  if not node:
    return {}
  ident = {}
  product = (node.get('_name') or '').strip()
  if product:
    ident['product'] = product
  for key, value in node.items():
    low = key.lower()
    if value and 'manufacturer' in low:
      ident.setdefault('manufacturer', str(value).strip())
    elif value and 'serial' in low:
      ident.setdefault('serial', str(value).strip())
  return ident

def gather_macos(args):
  """macOS cannot read the SD CID/CSD registers, so identity is limited to what the card reader reports"""
  autodetected = ''
  if not args.device and not args.dir:
    dev, mount = _autodetect_macos_target()
    if dev:
      autodetected = dev
      if mount:
        args.dir = mount        # point the benchmark/sweep at the card, not the boot disk's temp dir
  target = autodetected or args.device or args.dir or '/'
  info = diskutil_info(target)
  # An arbitrary subdirectory is neither a mount point nor a device (diskutil returns a null error plist), so
  # fall back to the device that backs it
  if not info.get('DeviceIdentifier'):
    device = _device_for_path(target)
    if device:
      info = diskutil_info(device)
  # Identity (media name, bus, removable, SMART, total capacity) lives on the whole-disk record, not the volume
  whole = diskutil_info(info.get('ParentWholeDisk', '')) if info.get('ParentWholeDisk') else {}
  if whole.get('DeviceIdentifier'):
    info = whole
  bus = info.get('BusProtocol', '')
  total = info.get('TotalSize', 0)
  block_size = info.get('DeviceBlockSize', 512) or 512
  sys_info = {
    'platform' : 'macos',
    'device' : info.get('DeviceIdentifier', target),
    'hardware' : {
      'model' : _sysctl('hw.model') or 'Mac',
      'serial_number' : '',
      'uuid' : ''
    },
    'software' : {
      'os_release' : 'macOS ' + (platform.mac_ver()[0] or ''),
      'os_kernel' : platform.release()
    },
    'storage' : {
      'type' : 'SD' if 'Secure Digital' in bus or 'SD' in bus else (bus or 'disk'),
      'label' : info.get('MediaName', '').strip() or 'unknown',
      'manufacturer' : 'unknown (macOS cannot read the SD CID registers)',
      'oem' : 'unknown',
      'speed_class' : [],
      'bus' : bus or 'unknown',
      'smart' : info.get('SMARTStatus', 'not available'),
      'blocks' : (total // block_size) if total else 0,
      'block_size' : block_size,
      'bytes' : total,
      'GB' : total / 1000000000,
      'GiB' : total / 1024 / 1024 / 1024,
      'state' : 'read only' if info.get('WritableMedia') is False else 'read/write',
      'removable_label' : 'removable' if info.get('RemovableMediaOrExternalDevice') else 'not removable',
      'cid_psn' : '', 'cid_mdt' : '', 'cid_prv_fw' : ''
    }
  }
  # A native SD slot can name the real card (product/make/serial) where diskutil only saw the reader; fill any
  # gaps it can, never overwriting something diskutil already resolved
  card = macos_card_identity(sys_info['device'])
  if card.get('product') and sys_info['storage']['label'] == 'unknown':
    sys_info['storage']['label'] = card['product']
  if card.get('manufacturer') and sys_info['storage']['manufacturer'].startswith('unknown'):
    sys_info['storage']['manufacturer'] = card['manufacturer']
  if card.get('serial') and not sys_info['storage']['cid_psn']:
    sys_info['storage']['cid_psn'] = card['serial']
  # Internal flag (not part of the JSON contract) so main() can tell the user which card it picked
  sys_info['_autodetected'] = autodetected
  # --raw: the whole diskutil record is the raw source on macOS (bytes/datetime values coerced to str for JSON)
  if args.raw:
    sys_info['raw'] = {'diskutil': {k: str(v) for k, v in info.items()}}
  return sys_info

def _sysctl(name):
  try:
    return subprocess.run(['sysctl', '-n', name], capture_output=True, encoding='utf-8', timeout=5).stdout.strip()
  except (subprocess.SubprocessError, OSError):
    return ''

#======================================
# Gather - Windows
#--------------------------------------

def _windows_volume(root):
  """Query the Win32 API for a drive's volume label, filesystem and removable flag. Returns a dict; any field we
  cannot read is simply omitted. Windows exposes no SD CID/CSD registers, so make/model stay unknown here too
  """
  info = {}
  try:
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    # DRIVE_REMOVABLE = 2 (a card reader / USB stick reports this)
    info['removable'] = kernel32.GetDriveTypeW(root) == 2
    label = ctypes.create_unicode_buffer(261)
    fs = ctypes.create_unicode_buffer(261)
    serial = wintypes.DWORD()
    if kernel32.GetVolumeInformationW(root, label, 261, ctypes.byref(serial), None, None, fs, 261):
      info['label'] = label.value
      info['filesystem'] = fs.value
      info['volume_serial'] = f'{serial.value:08X}'
  except Exception:
    pass
  return info

def gather_windows(args):
  """Windows cannot read the SD CID/CSD registers, so identity is limited to the drive's capacity, volume label
  and removable state. Resolve the target down to its drive root (e.g. 'E:\\') for the Win32 queries
  """
  target = args.dir or args.device or os.getcwd()
  drive = os.path.splitdrive(os.path.abspath(target))[0]        # 'E:' from 'E:\path'
  root = (drive + os.sep) if drive else os.path.abspath(os.sep)
  vol = _windows_volume(root)

  try:
    import shutil
    total = shutil.disk_usage(root).total
  except OSError:
    total = 0
  block_size = 512

  sys_info = {
    'platform' : 'windows',
    'device' : drive or root,
    'hardware' : {
      'model' : platform.uname().machine or 'PC',
      'serial_number' : '',
      'uuid' : ''
    },
    'software' : {
      'os_release' : platform.system() + ' ' + platform.release(),
      'os_kernel' : platform.version()
    },
    'storage' : {
      'type' : 'SD/removable' if vol.get('removable') else 'disk',
      'label' : vol.get('label') or 'unknown',
      'manufacturer' : 'unknown (Windows cannot read the SD CID registers)',
      'oem' : 'unknown',
      'speed_class' : [],
      'filesystem_type' : vol.get('filesystem', ''),
      'volume_serial' : vol.get('volume_serial', ''),
      'blocks' : (total // block_size) if total else 0,
      'block_size' : block_size,
      'bytes' : total,
      'GB' : total / 1000000000,
      'GiB' : total / 1024 / 1024 / 1024,
      'state' : 'read/write',
      'removable_label' : 'removable' if vol.get('removable') else 'not removable',
      'cid_psn' : '', 'cid_mdt' : '', 'cid_prv_fw' : ''
    }
  }
  # --raw: the Win32 volume query plus the disk-usage total are the raw source on Windows
  if args.raw:
    sys_info['raw'] = {'volume': vol, 'disk_total_bytes': total}
  return sys_info

#======================================
# Report - print the gathered detail
#--------------------------------------

def render_report(console, sys_info):
  """Render the full human-readable report - identity, hardware, storage facts and consistency findings."""
  storage = sys_info['storage']
  hardware = sys_info['hardware']
  software = sys_info['software']
  platform_name = sys_info['platform']

  # System
  console.section('System')
  console.kv('Model', hardware['model'], value_style='bold')
  if hardware['serial_number']:
    console.kv('Serial', hardware['serial_number'])
  console.kv('OS', software['os_release'], note='kernel ' + software['os_kernel'])
  uptime = read_file('/proc/uptime', '\n')                # Linux only; returns '' (skipped) elsewhere
  if uptime:
    console.kv('Uptime', str(datetime.timedelta(seconds=int(float(uptime.split()[0])))))
  if platform_name == 'linux':
    console.kv('Ethernet MAC', hardware['mac_eth0'])
    console.kv('Wi-Fi MAC', hardware['mac_wlan0'])
    console.kv('Bluetooth MAC', hardware['mac_bt0'])

  # Storage identity
  console.section('Storage', note=storage['type'])
  console.kv('Model', storage['label'], value_style='bold')
  capacity_note = f_num(storage['GiB'], 1) + ' GiB ' + console.g['dot'] + ' ' + f_num(storage['blocks']) + ' × ' + f_num(storage['block_size']) + ' B'
  console.kv('Capacity', f_num(storage['GB'], 1) + ' GB', note=capacity_note)
  if storage.get('speed_class'):
    console.kv('Rated class', ', '.join(storage['speed_class']), value_style='cyan')

  if platform_name == 'linux':
    console.kv('Make', storage['manufacturer'])
    if storage.get('oem') and storage['oem'] != storage['manufacturer']:
      console.kv('OEM', storage['oem'])
    console.kv('Serial (CID)', storage['cid_psn'] or 'n/a')
    console.kv('Made (mm/yyyy)', storage['cid_mdt'] or 'n/a')
    console.kv('Firmware rev', storage['cid_prv_fw'] or 'n/a')
    console.kv('Access', storage['state'] + ' ' + console.g['dot'] + ' ' + storage['removable_label'])

    # Registers - only show the ones the card actually populated
    registers = [('OCR', 'ocr'), ('CID', 'cid'), ('CSD', 'csd'), ('RCA', 'rca'),
                 ('DSR', 'dsr'), ('SCR', 'scr'), ('SSR', 'ssr')]
    present = [(name, storage[key]) for name, key in registers if storage.get(key)]
    if present:
      console.section('Registers')
      for name, value in present:
        console.kv(name, value, width=6, value_style='grey')

    # Filesystem
    fs = sys_info['filesystem']
    console.section('Filesystem', note=sys_info['partition'])
    console.kv('State', fs['state'])
    console.kv('Created', fs['created'])
    console.kv('Last checked', fs['last_checked'])
    console.kv('Mounted', f_num(fs['mount_count']) + ' times', note='last: ' + fs['last_mount'])
    _render_linux_stats(console, sys_info)
  elif platform_name == 'macos':
    console.kv('Bus', storage.get('bus', 'unknown'))
    console.kv('SMART', storage.get('smart', 'n/a'))
    console.kv('Access', storage['state'] + ' ' + console.g['dot'] + ' ' + storage['removable_label'])
    console.line(console.style('macOS cannot read the SD CID/CSD registers - make/model and rated class are', 'grey'), indent=2)
    console.line(console.style('unknown here. Run on a Raspberry Pi for full identity.', 'grey'), indent=2)
  else:  # windows
    if storage.get('filesystem_type'):
      console.kv('Filesystem', storage['filesystem_type'])
    if storage.get('volume_serial'):
      console.kv('Volume serial', storage['volume_serial'])
    console.kv('Access', storage['state'] + ' ' + console.g['dot'] + ' ' + storage['removable_label'])
    console.line(console.style('Windows cannot read the SD CID/CSD registers - make/model and rated class are', 'grey'), indent=2)
    console.line(console.style('unknown here. Run on a Raspberry Pi for full identity.', 'grey'), indent=2)

  render_consistency(console, sys_info)

def render_consistency(console, sys_info):
  """Show the decoded CSD summary and any cross-check findings. Self-skips when the CSD could not be read (macOS
  / Windows) and there is nothing to report, so it is safe to call on every platform
  """
  consistency = sys_info.get('consistency', {})
  decoded = sys_info.get('storage', {}).get('csd_decoded')
  findings = consistency.get('findings', [])
  if not decoded and not findings:
    return

  console.section('Consistency', note='decoded from the CSD register ' + console.g['dot'] + ' cross-checked against the branding')
  if decoded:
    capacity = f_num(decoded['capacity_bytes'] / 1000 ** 3, 1) + ' GB' if decoded.get('capacity_bytes') else 'unknown'
    console.kv('CSD says', decoded['capacity_type'] + ' ' + console.g['dot'] + ' ' + capacity,
               note='max ' + f_num(decoded['tran_speed_mbit'], 0) + ' Mbit/s')
  for finding in findings:
    kind = {'fail': 'fail', 'warn': 'warn', 'info': 'info'}.get(finding['severity'], 'info')
    console.line(console.badge(finding['severity'].upper(), kind) + ' ' + finding['message'])
  if decoded and not findings:
    console.line(console.badge('OK', 'pass') + ' CSD, capacity and branding are internally consistent')

def render_raw(console, sys_info):
  """--raw debug dump: the decoded CSD, every unparsed source we read, and the raw per-run benchmark samples. This
  is the verbatim detail behind the friendly report - the first thing to reach for when a parse looks wrong
  """
  console.section('Raw', note='verbatim sources for debugging')

  decoded = sys_info.get('storage', {}).get('csd_decoded')
  if decoded:
    console.kv('CSD decoded', '', label_style='grey')
    for key in sorted(decoded):
      console.line(console.style((str(key) + ':').ljust(20), 'grey') + str(decoded[key]), indent=4)

  perf = sys_info.get('perf')
  if perf:
    console.kv('Benchmark samples', '', label_style='grey')
    console.line(console.style('seq write MBps:  ', 'grey') + '  '.join(f_num(v, 1) for v in perf['write']['seq_mbps']), indent=4)
    console.line(console.style('rand write IOPS: ', 'grey') + '  '.join(f_num(v, 0) for v in perf['write']['rand_4kb_iops']), indent=4)
    console.line(console.style('rand read IOPS:  ', 'grey') + '  '.join(f_num(v, 0) for v in perf['read']['rand_4kb_iops']), indent=4)

    # Latency distribution (ms per op) - the tail a mean hides, aggregated across every run
    console.kv('Benchmark latency', 'ms per op, aggregated across runs', label_style='grey')
    phases = (('seq write ', perf['write'].get('seq_latency_pct', [])),
              ('rand write', perf['write'].get('rand_4kb_latency_pct', [])),
              ('rand read ', perf['read'].get('rand_4kb_latency_pct', [])))
    for label, pct_list in phases:
      lat = sdbench.aggregate_latency(pct_list)
      console.line(console.style(label + ':  ', 'grey')
                   + 'p50 ' + f_num(lat['p50_ms'], 2) + '  ' + console.g['dot']
                   + ' p95 ' + f_num(lat['p95_ms'], 2) + '  ' + console.g['dot']
                   + ' p99 ' + f_num(lat['p99_ms'], 2) + '  ' + console.g['dot']
                   + ' max ' + f_num(lat['max_ms'], 2), indent=4)

  for name, value in sys_info.get('raw', {}).items():
    console.kv(name, '', label_style='grey')
    if isinstance(value, dict):
      for key in value:
        console.line(console.style((str(key) + ':').ljust(20), 'grey') + str(value[key]), indent=4)
    else:
      for text_line in str(value).rstrip('\n').split('\n'):
        console.line(console.style(text_line, 'grey'), indent=4)

def _render_linux_stats(console, sys_info):
  cpu = sys_info['stats']['cpu']
  memory = sys_info['stats']['memory']
  disk = sys_info['stats']['disk']

  console.section('Live stats')
  load = f_num(cpu['load_1m'], 2) + '  ' + f_num(cpu['load_5m'], 2) + '  ' + f_num(cpu['load_15m'], 2)
  console.kv('Load 1/5/15m', load,
             value_style='yellow' if cpu['load_high'] else None,
             note='high load may skew the benchmark' if cpu['load_high'] else '')
  console.kv('Threads', cpu['threads'])
  console.kv('Memory', f_num(memory['free']) + ' / ' + f_num(memory['total']) + ' MiB free')
  console.kv('Swap', f_num(memory['swap_free']) + ' / ' + f_num(memory['swap_total']) + ' MiB free')
  console.kv('Disk reads', f_num(disk['read_completed']) + ' ops ' + console.g['dot'] + ' ' + f_num(disk['read_avg_mbps'], 1) + ' MBps ' + console.g['dot'] + ' ' + f_num(disk['read_avg_iops']) + ' IOPS')
  console.kv('Disk writes', f_num(disk['write_completed']) + ' ops ' + console.g['dot'] + ' ' + f_num(disk['write_avg_mbps'], 1) + ' MBps ' + console.g['dot'] + ' ' + f_num(disk['write_avg_iops']) + ' IOPS')

#======================================
# Performance test (native, see bench.py)
#--------------------------------------

def compute_perf(sys_info, args, spinner, progress):
  """Run the native benchmark, streaming per-run progress to `progress` (a Console), and stash the results plus
  the best-half medians on sys_info. No grading here - see compute_grade()
  """
  bench_dir = args.dir or ('/var/tmp' if sys_info['platform'] == 'linux' else tempfile.gettempdir())
  test_file = os.path.join(bench_dir, test_file_name)
  size_bytes = args.size_mb * 1024 * 1024

  progress.section('Benchmark', note=str(args.size_mb) + ' MiB in ' + bench_dir + ' ' + progress.g['dot'] + ' ' + str(args.runs) + ' runs ' + progress.g['dot'] + ' non-destructive')

  def on_phase(run_number, name):
    spinner.update('Run ' + str(run_number) + '/' + str(args.runs) + '  ' + name + '…')

  def on_run(run_number, metrics):
    spinner.clear()
    sw, rw, rr = metrics['seq_write'], metrics['rand_write'], metrics['rand_read']
    progress.line('Run ' + str(run_number) + '/' + str(args.runs) + '   '
                  + progress.style('seq', 'grey') + ' ' + ('%7.1f' % sw['mbps']) + ' MBps   '
                  + progress.style('wr', 'grey') + ' ' + ('%6.0f' % rw['iops']) + ' IOPS   '
                  + progress.style('rd', 'grey') + ' ' + ('%6.0f' % rr['iops']) + ' IOPS')

  try:
    perf = sdbench.run(test_file, args.runs, size_bytes, args.seconds, on_run=on_run, on_phase=on_phase)
  finally:
    spinner.stop()
    if os.path.isfile(test_file):
      os.remove(test_file)
  sys_info['perf'] = perf

  # Best guess of real world performance: median of the best half of runs (drops slow outliers)
  perf['write']['seq_mbps_result'] = best_median(perf['write']['seq_mbps'])
  perf['write']['rand_4kb_iops_result'] = best_median(perf['write']['rand_4kb_iops'])
  perf['read']['rand_4kb_iops_result'] = best_median(perf['read']['rand_4kb_iops'])
  return perf

def render_benchmark(console, sys_info):
  """The headline result table: best-half median plus mean and standard deviation over all runs"""
  perf = sys_info['perf']
  console.section('Result', note='best-half median ' + console.g['dot'] + ' mean ' + console.g['dot'] + ' stdev over all runs')
  _render_metric(console, 'Sequential write', perf['write']['seq_mbps'], 'MBps', 1)
  _render_metric(console, 'Random 4K write', perf['write']['rand_4kb_iops'], 'IOPS', 0)
  _render_metric(console, 'Random 4K read', perf['read']['rand_4kb_iops'], 'IOPS', 0)

def _render_metric(console, label, samples, units, dec):
  stdev = statistics.stdev(samples) if len(samples) > 1 else 0
  value = f_num(best_median(samples), dec) + ' ' + units
  note = 'mean ' + f_num(statistics.mean(samples), dec) + ' ' + console.g['dot'] + ' sd ' + f_num(stdev, dec)
  console.kv(label, value, value_style='bold', note=note)

#======================================
# Grade the results against the rated speed class
#--------------------------------------

def compute_grade(sys_info):
  """Compare the measured medians against the toughest target implied by the card's declared speed class(es),
  falling back to A1 (the Raspberry Pi baseline) when no class is known. Returns a structured grade and stores
  it on sys_info - no printing here, so it is reused by both the text and JSON renderers
  """
  perf = sys_info['perf']
  declared_classes = sys_info['storage'].get('speed_class', [])

  target = {'seq_write': 0, 'rand_read': 0, 'rand_write': 0}
  for card_class in declared_classes:
    class_spec = speed_class.get(card_class, {})
    for metric in target:
      target[metric] = max(target[metric], class_spec.get(metric, 0))
  for metric in target:
    if target[metric] == 0:
      target[metric] = speed_class['A1'][metric]

  def metric(measured, want, units):
    return {'measured': measured, 'target': want, 'units': units, 'pass': measured >= want}

  metrics = {
    'seq_write': metric(perf['write']['seq_mbps_result'], target['seq_write'], 'MBps'),
    'rand_write': metric(perf['write']['rand_4kb_iops_result'], target['rand_write'], 'IOPS'),
    'rand_read': metric(perf['read']['rand_4kb_iops_result'], target['rand_read'], 'IOPS'),
  }
  grade = {
    'graded_against': ', '.join(declared_classes) if declared_classes else 'A1',
    'assumed': not declared_classes,
    'targets': target,
    'metrics': metrics,
    'pass': all(m['pass'] for m in metrics.values()),
  }
  sys_info['grade'] = grade
  return grade

def render_grade(console, sys_info):
  """Render the performance grade section - measured medians against the target implied by the rated class."""
  grade = sys_info['grade']
  note = 'vs ' + grade['graded_against'] + (' (assumed - no rated class known)' if grade['assumed'] else '')
  console.section('Grade', note=note)

  order = [('seq_write', 'Sequential write'), ('rand_write', 'Random 4K write'), ('rand_read', 'Random 4K read')]
  for key, label in order:
    m = grade['metrics'][key]
    fraction = (m['measured'] / m['target']) if m['target'] else 1.0
    bar = console.bar(fraction)
    verdict = console.badge('PASS' if m['pass'] else 'FAIL', 'pass' if m['pass'] else 'fail')
    value = (f_num(m['measured'], 1) + ' ' + m['units']).ljust(14)
    goal = ('target ' + f_num(m['target'], 0) + ' ' + m['units']).ljust(20)
    console.line(console.style((label + ':').ljust(18), 'grey') + value + bar + '  ' + console.style(goal, 'grey') + verdict)

  if not grade['metrics']['seq_write']['pass']:
    console.out('')
    console.line(console.style('Note: sequential write slows as a card wears - a reformat may help.', 'grey'))

  console.out('')
  if grade['pass']:
    console.box('PASS  ' + console.g['dot'] + '  meets its rated ' + grade['graded_against'] + ' performance', 'pass')
  else:
    console.box('FAIL  ' + console.g['dot'] + '  slower than rated ' + grade['graded_against'] + ' (worn, misbranded, or fake)', 'fail')

#======================================
# Capacity-fraud sweep (native, see verify.py)
#--------------------------------------

def _human_bytes(num_bytes):
  """Base-10 sizes, matching how cards are branded (and sdverify's own formatting)"""
  value = float(num_bytes)
  for unit in ('B', 'kB', 'MB', 'GB', 'TB'):
    if abs(value) < 1000 or unit == 'TB':
      return ('%.0f %s' % (value, unit)) if unit == 'B' else ('%.2f %s' % (value, unit))
    value /= 1000
  return '%.2f TB' % value

def confirm_capacity_sweep(args, sys_info, out, interactive):
  """The sweep fills the card's free space and writes its full capacity once, so it is gated. Returns True to
  proceed. --yes always proceeds; when non-interactive (piped, --json, --quiet) we require --yes and refuse
  otherwise rather than block on a prompt that no one can answer
  """
  if args.yes:
    return True
  if not interactive:
    out.out(out.badge('SKIP', 'warn') + ' Capacity sweep needs confirmation: re-run with --yes (it fills free space and adds flash wear).')
    return False
  target = _human_bytes(args.capacity_mb * 1024 * 1024) if args.capacity_mb else 'all free space'
  out.out('')
  out.line(out.style('Capacity sweep will WRITE ' + target + ' to ' + (args.dir or 'the card') + ', then read it back.', 'yellow'))
  out.line(out.style('Existing files are untouched, but this takes time and adds flash wear.', 'grey'))
  try:
    answer = input('  Proceed? [y/N] ').strip().lower()
  except (EOFError, KeyboardInterrupt):
    answer = ''
  return answer in ('y', 'yes')

def compute_capacity(sys_info, args, spinner, progress):
  """Run the write-then-verify sweep against the card, streaming progress, and stash the result on sys_info.
  Non-destructive to existing files; the sweep's own test files are always cleaned up
  """
  sweep_dir = args.dir or ('/var/tmp' if sys_info['platform'] == 'linux' else tempfile.gettempdir())
  cap = args.capacity_mb * 1024 * 1024 if args.capacity_mb is not None else None

  progress.section('Capacity sweep', note='write + verify in ' + sweep_dir + ' ' + progress.g['dot'] + ' unmasks fake cards')

  def on_phase(name):
    spinner.update({'plan': 'Planning sweep…', 'write': 'Writing test data across the card…',
                    'verify': 'Reading it back and verifying…', 'cleanup': 'Cleaning up test files…'}.get(name, name))

  def on_progress(phase, done, total):
    if not total:
      return
    pct = 100.0 * done / total
    spinner.update(('Writing' if phase == 'write' else 'Verifying') + ' '
                   + ('%.0f%%' % pct) + '  ' + _human_bytes(done) + ' / ' + _human_bytes(total))

  try:
    capacity = sdverify.run(sweep_dir, cap, on_progress=on_progress, on_phase=on_phase)
  finally:
    spinner.stop()
  sys_info['capacity'] = capacity
  return capacity

def render_capacity(console, sys_info):
  """Render the capacity-sweep (fake-card test) section - written vs verified bytes and the verdict."""
  cap = sys_info['capacity']
  console.section('Capacity', note='write + verify sweep (fake-card test)')
  console.kv('Reported capacity', _human_bytes(cap['reported_total_bytes']))
  swept = _human_bytes(cap['swept_bytes']) + (' ' + console.g['dot'] + ' stopped early (filesystem full)' if cap['short'] else '')
  console.kv('Swept free space', swept)
  console.kv('Verified good', _human_bytes(cap['verified_bytes']))
  if cap['first_bad_offset'] is not None:
    console.kv('First bad offset', _human_bytes(cap['first_bad_offset']), value_style='red')
    console.kv('Usable estimate', _human_bytes(cap['usable_estimate_bytes']), value_style='red')
  console.out('')
  if cap['ok']:
    console.box('GENUINE  ' + console.g['dot'] + '  every written byte read back correctly', 'pass')
  elif cap['swept_bytes'] == 0:
    console.line(console.style('Sweep did not run: ' + cap['reason'], 'yellow'))
  else:
    console.box('FAKE  ' + console.g['dot'] + '  card is smaller than it reports (or failing)', 'fail')

#======================================
# JSON (machine-readable) output
#--------------------------------------

def build_json(sys_info):
  """Assemble the machine-readable document in a stable key order. --format json emits exactly this on stdout so
  other software and scripts can consume identity, benchmark samples, and the grade
  """
  doc = {'schema': SCHEMA, 'tool_version': VERSION, 'generated': sys_info['generated']}
  for key in ('platform', 'device', 'partition', 'hardware', 'software', 'storage', 'filesystem', 'stats'):
    if key in sys_info:
      doc[key] = sys_info[key]
  if 'perf' in sys_info:
    doc['benchmark'] = sys_info['perf']
  if 'grade' in sys_info:
    doc['grade'] = sys_info['grade']
  if 'capacity' in sys_info:
    doc['capacity'] = sys_info['capacity']
  if 'consistency' in sys_info:
    doc['consistency'] = sys_info['consistency']
  if 'raw' in sys_info:
    doc['raw'] = sys_info['raw']
  return doc

#======================================
# Persist a run to a local SQLite database (--save-db)
#--------------------------------------

# One row per run. The full JSON document is stored verbatim in `document`; the rest are pulled out as typed
# columns so the DB is queryable (e.g. every fake ever seen, or all runs for one card serial) without parsing
# JSON in SQL. (name, SQLite type-affinity) pairs, in insert order
DB_COLUMNS = (
  ('generated', 'TEXT'), ('tool_version', 'TEXT'), ('schema', 'TEXT'), ('platform', 'TEXT'),
  ('host_uuid', 'TEXT'), ('device', 'TEXT'), ('card_label', 'TEXT'), ('card_type', 'TEXT'),
  ('manufacturer', 'TEXT'), ('oem', 'TEXT'), ('cid_psn', 'TEXT'), ('cid_mdt', 'TEXT'),
  ('capacity_gb', 'REAL'), ('speed_class', 'TEXT'), ('csd_capacity_type', 'TEXT'), ('csd_capacity_gb', 'REAL'),
  ('seq_write_mbps', 'REAL'), ('rand_write_iops', 'REAL'), ('rand_read_iops', 'REAL'),
  ('grade_pass', 'INTEGER'), ('graded_against', 'TEXT'), ('capacity_ok', 'INTEGER'),
  ('consistency_ok', 'INTEGER'), ('overall_pass', 'INTEGER'), ('document', 'TEXT'),
)
DB_COLUMN_NAMES = tuple(name for name, _ in DB_COLUMNS)

def _db_row(sys_info, overall_pass):
  """Flatten the gathered result into the DB_COLUMNS. Everything is .get()-guarded so a --no-benchmark run, or a
  macOS/Windows run with no registers, still stores a clean partial row rather than crashing
  """
  storage = sys_info.get('storage', {})
  perf = sys_info.get('perf', {})
  grade = sys_info.get('grade', {})
  decoded = storage.get('csd_decoded') or {}
  def bool_or_none(flag):
    return (1 if flag else 0) if flag is not None else None
  return {
    'generated': sys_info.get('generated'),
    'tool_version': VERSION,
    'schema': SCHEMA,
    'platform': sys_info.get('platform'),
    'host_uuid': sys_info.get('hardware', {}).get('uuid') or None,
    'device': sys_info.get('device'),
    'card_label': storage.get('label'),
    'card_type': storage.get('type'),
    'manufacturer': storage.get('manufacturer'),
    'oem': storage.get('oem'),
    'cid_psn': storage.get('cid_psn') or None,
    'cid_mdt': storage.get('cid_mdt') or None,
    'capacity_gb': storage.get('GB'),
    'speed_class': ', '.join(storage.get('speed_class', [])) or None,
    'csd_capacity_type': decoded.get('capacity_type'),
    'csd_capacity_gb': (decoded['capacity_bytes'] / 1000 ** 3) if decoded.get('capacity_bytes') else None,
    'seq_write_mbps': perf.get('write', {}).get('seq_mbps_result'),
    'rand_write_iops': perf.get('write', {}).get('rand_4kb_iops_result'),
    'rand_read_iops': perf.get('read', {}).get('rand_4kb_iops_result'),
    'grade_pass': bool_or_none(grade.get('pass')) if grade else None,
    'graded_against': grade.get('graded_against'),
    'capacity_ok': bool_or_none(sys_info['capacity']['ok']) if 'capacity' in sys_info else None,
    'consistency_ok': bool_or_none(sys_info['consistency']['ok']) if 'consistency' in sys_info else None,
    'overall_pass': bool_or_none(overall_pass),
    'document': json.dumps(build_json(sys_info), default=str),
  }

def save_to_db(path, sys_info, overall_pass):
  """Append this run to a local SQLite database, creating it (and its parent directory) on first use. The DB is
  local-only, so it keeps the real serial/MACs - the anonymisation caveat in ROADMAP applies only to upload
  """
  directory = os.path.dirname(path)
  if directory:
    os.makedirs(directory, exist_ok=True)
  row = _db_row(sys_info, overall_pass)
  columns = ', '.join(DB_COLUMN_NAMES)
  placeholders = ', '.join(':' + name for name in DB_COLUMN_NAMES)
  schema = ', '.join(name + ' ' + kind for name, kind in DB_COLUMNS)
  with sqlite3.connect(path) as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY AUTOINCREMENT, ' + schema + ')')
    conn.execute('INSERT INTO runs (' + columns + ') VALUES (' + placeholders + ')', row)
  return path

def query_db(path):
  """Summarise the saved run history: totals, and one grouped row per distinct card (by label + CID serial) with
  its run count, best sequential write, latest verdict, plus every failing run. Returns None if the DB has no
  runs table yet (created by --save-db). Raises sqlite3.Error on a corrupt/unreadable file
  """
  conn = sqlite3.connect(path)
  conn.row_factory = sqlite3.Row
  try:
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='runs'").fetchone():
      return None
    total = conn.execute('SELECT count(*) FROM runs').fetchone()[0]
    passed = conn.execute('SELECT count(*) FROM runs WHERE overall_pass = 1').fetchone()[0]
    failed = conn.execute('SELECT count(*) FROM runs WHERE overall_pass = 0').fetchone()[0]
    period = conn.execute('SELECT min(generated), max(generated) FROM runs').fetchone()
    # min(overall_pass) over a card's runs is 0 if it ever failed, so it doubles as an "ever failed?" flag
    cards = conn.execute(
      'SELECT card_label, cid_psn, count(*) AS runs, max(generated) AS last_seen, '
      'max(seq_write_mbps) AS best_seq, min(overall_pass) AS all_pass, '
      'max(capacity_gb) AS capacity_gb, max(speed_class) AS speed_class '
      'FROM runs GROUP BY card_label, cid_psn ORDER BY last_seen DESC').fetchall()
    flagged = conn.execute(
      'SELECT generated, card_label, cid_psn, grade_pass, capacity_ok, consistency_ok '
      'FROM runs WHERE overall_pass = 0 ORDER BY generated DESC').fetchall()
    return {
      'path': path, 'total': total, 'passed': passed, 'failed': failed,
      'cards_count': len(cards), 'first': period[0], 'last': period[1],
      'cards': [dict(row) for row in cards], 'flagged': [dict(row) for row in flagged],
    }
  finally:
    conn.close()

def _flag_reason(record):
  """Turn a failing run's pass/fail columns into a human reason. grade/capacity/consistency map to the three tests"""
  reasons = []
  if record.get('grade_pass') == 0:
    reasons.append('too slow')
  if record.get('capacity_ok') == 0:
    reasons.append('capacity fraud')
  if record.get('consistency_ok') == 0:
    reasons.append('CSD/CID inconsistent')
  return ', '.join(reasons) or 'failed'

def render_db_summary(console, data):
  """Render the saved-history summary - totals, one row per distinct card, and any failing runs."""
  console.section('Database', note=data['path'])
  console.kv('Runs recorded', f_num(data['total']))
  console.kv('Distinct cards', f_num(data['cards_count']))
  if data['total']:
    console.kv('Period', (data['first'] or '?') + ' ' + console.g['dot'] + ' ' + (data['last'] or '?'))
    console.kv('Verdict', console.badge('PASS', 'pass') + ' ' + f_num(data['passed']) + '   '
               + console.badge('FAIL', 'fail') + ' ' + f_num(data['failed']))

  if data['cards']:
    console.section('Cards', note='most recently tested first')
    for card in data['cards']:
      verdict = console.badge('PASS', 'pass') if card['all_pass'] else console.badge('FAIL', 'fail')
      label = (card['card_label'] or 'unknown')
      if card['cid_psn']:
        label += ' (' + card['cid_psn'] + ')'
      note = f_num(card['runs']) + '× ' + console.g['dot'] + ' last ' + (card['last_seen'] or '?')[:10]
      if card['best_seq']:
        note += ' ' + console.g['dot'] + ' best ' + f_num(card['best_seq'], 1) + ' MBps'
      if card['speed_class']:
        note += ' ' + console.g['dot'] + ' ' + card['speed_class']
      console.kv(label, verdict, width=28, value_style=None, note=note)

  if data['flagged']:
    console.section('Flagged runs', note='failed a test - suspect worn, misbranded, or fake')
    for record in data['flagged']:
      label = (record['card_label'] or 'unknown')
      if record['cid_psn']:
        label += ' (' + record['cid_psn'] + ')'
      console.line(console.badge('FAIL', 'fail') + ' ' + (record['generated'] or '?')[:10] + '  '
                   + label + ' ' + console.g['dot'] + ' ' + console.style(_flag_reason(record), 'yellow'))

def run_db_query(path, out, errs, json_mode):
  """Handle --db-query: print a summary of the saved history and exit, without testing a card"""
  if not os.path.exists(path):
    errs.out(errs.badge('FAIL', 'fail') + ' No database at ' + path + ' yet - run with --save-db first.')
    return 2
  try:
    data = query_db(path)
  except sqlite3.Error as error:
    errs.out(errs.badge('FAIL', 'fail') + ' Could not read the database ' + path + ': ' + str(error))
    return 2
  if data is None:
    errs.out(errs.badge('FAIL', 'fail') + ' ' + path + ' has no rpi-sdinfo run history yet.')
    return 2
  if json_mode:
    print(json.dumps(data, indent=2, default=str))
  else:
    out.banner('rpi-sdinfo ' + VERSION, 'saved run history')
    render_db_summary(out, data)
    out.out('')
  return 0

#======================================
# Main
#--------------------------------------

def parse_args(argv=None):
  """Build the rpi-sdinfo argument parser and parse argv (defaults to sys.argv)."""
  parser = argparse.ArgumentParser(description='Identify, benchmark, and grade an SD/MMC card (Raspberry Pi Linux, macOS, or Windows).')
  parser.add_argument('--device', help='Storage device to inspect. Linux: block device name (default: ' + block_device + '). macOS: disk id or mount path (e.g. disk4 or /Volumes/CARD). Windows: a drive (e.g. E:)')
  parser.add_argument('--partition', help='Linux filesystem partition to inspect (default: <device>p2)')
  parser.add_argument('--dir', help='Directory on the card to benchmark (default: /var/tmp on Linux, system temp dir on macOS/Windows). Point this at the mounted card, e.g. /Volumes/CARD or E:\\')
  parser.add_argument('--runs', type=int, default=max_runs, help='Number of benchmark runs to average (default: %(default)s)')
  parser.add_argument('--size-mb', type=int, default=sdbench.DEFAULT_SIZE_MB, help='Test file size in MiB (default: %(default)s)')
  parser.add_argument('--seconds', type=int, default=sdbench.DEFAULT_SECONDS, help='Duration of each random IO test (default: %(default)s)')
  parser.add_argument('--no-benchmark', action='store_true', help='Only gather and print card detail, skip the performance test')
  parser.add_argument('--capacity-check', action='store_true', help='Also run a capacity-fraud sweep (fills free space, writes+verifies to unmask fake cards). Slow; adds flash wear')
  parser.add_argument('--capacity-mb', type=int, default=None, help='Cap the capacity sweep to this many MiB instead of filling all free space (for a quick partial check)')
  parser.add_argument('--yes', action='store_true', help='Skip the confirmation prompt for the capacity sweep (required when non-interactive, e.g. with --json or --quiet)')
  parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format (default: %(default)s). json emits the full result on stdout for other tools')
  parser.add_argument('--json', action='store_const', const='json', dest='format', help='Shortcut for --format json')
  parser.add_argument('--quiet', action='store_true', help='Suppress the report; exit code still reflects PASS/FAIL (handy in scripts)')
  parser.add_argument('--raw', action='store_true', help='Also dump the verbatim sources (full dumpe2fs / registers / diskutil, decoded CSD, raw benchmark samples) for debugging - a RAW report section, and a "raw" block in --json')
  parser.add_argument('--save-db', nargs='?', const=default_db, default=None, metavar='PATH', help='Append this run to a local SQLite database (default: ' + default_db + '). Builds a queryable history of every card tested; local-only, so decide what is safe before sharing it')
  parser.add_argument('--db-query', nargs='?', const=default_db, default=None, metavar='PATH', help='Summarise the saved run history from a local SQLite database (default: ' + default_db + ') and exit, instead of testing a card. Honours --json')
  color = parser.add_mutually_exclusive_group()
  color.add_argument('--color', dest='color', action='store_const', const=True, help='Force colour output (also: CLICOLOR_FORCE=1)')
  color.add_argument('--no-color', dest='color', action='store_const', const=False, help='Disable colour output (also: NO_COLOR=1)')
  parser.set_defaults(color=None)
  parser.add_argument('--version', action='version', version='rpi-sdinfo ' + VERSION)
  return parser.parse_args(argv)

def gather(args):
  """Dispatch to the right platform collector. Returns None on an unsupported platform"""
  if sys.platform == 'darwin':
    return gather_macos(args)
  if sys.platform.startswith('linux'):
    return gather_linux(args)
  if sys.platform == 'win32':
    return gather_windows(args)
  return None

def main(argv=None):
  """rpi-sdinfo entry point: gather, benchmark, verify and render, returning the process exit code."""
  args = parse_args(argv)
  # Set the locale for number formatting once we are actually running (not at import)
  locale.setlocale(locale.LC_ALL, '')

  json_mode = args.format == 'json'
  # stdout carries the report (text) or the JSON document; progress and messages go to stderr in JSON mode so
  # `--format json` stays pipe-clean. --quiet routes progress to the void but keeps the exit code meaningful
  out = ui.Console(sys.stdout, color=args.color)
  errs = ui.Console(sys.stderr, color=args.color)
  if json_mode:
    progress = errs
  elif args.quiet:
    progress = ui.Console(open(os.devnull, 'w'), color=False)
  else:
    progress = out
  spinner = ui.Spinner(progress)

  # --db-query short-circuits: summarise the saved history and exit, no card required
  if args.db_query is not None:
    return run_db_query(args.db_query, out, errs, json_mode)

  sys_info = gather(args)
  if sys_info is None:
    errs.out(errs.badge('FAIL', 'fail') + ' Unsupported platform: ' + sys.platform
             + '. This tool supports Linux (Raspberry Pi), macOS, and Windows.')
    return 2
  sys_info['generated'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

  # Tell the user when we auto-picked a removable card (no --device/--dir was given) so the target isn't a mystery
  if sys_info.get('_autodetected'):
    progress.out(progress.badge('INFO', 'info') + ' Auto-selected removable card ' + sys_info['_autodetected']
                 + (' (' + args.dir + ')' if args.dir else '') + ' - pass --device/--dir to override')

  # Decode the CSD and cross-check the card's self-declared facts (instant, non-destructive; no-op off Linux)
  compute_consistency(sys_info)

  if not json_mode and not args.quiet:
    out.banner('rpi-sdinfo ' + VERSION, 'SD/MMC identity ' + out.g['dot'] + ' benchmark ' + out.g['dot'] + ' grade')
    render_report(out, sys_info)

  # Each test computes (streaming live progress) then renders its result table straight after, so in text mode
  # the progress and the result for one test stay grouped rather than all-progress-then-all-results
  render = not json_mode and not args.quiet

  if not args.no_benchmark:
    try:
      compute_perf(sys_info, args, spinner, progress)
    except OSError as error:
      errs.out('')
      errs.out(errs.badge('FAIL', 'fail') + ' Could not benchmark ' + (args.dir or 'the default directory') + ': ' + str(error))
      return 2
    compute_grade(sys_info)
    if render:
      render_benchmark(out, sys_info)
      render_grade(out, sys_info)

  # Optional, opt-in capacity-fraud sweep. Gated behind a confirmation (or --yes) because it fills free space
  if args.capacity_check:
    interactive = sys.stdin.isatty() and not json_mode and not args.quiet
    if confirm_capacity_sweep(args, sys_info, errs if json_mode else progress, interactive):
      try:
        compute_capacity(sys_info, args, spinner, progress)
      except OSError as error:
        errs.out('')
        errs.out(errs.badge('FAIL', 'fail') + ' Capacity sweep failed on ' + (args.dir or 'the default directory') + ': ' + str(error))
        return 2
      if render:
        render_capacity(out, sys_info)

  # --raw debug dump goes last in the text report, after the friendly sections it explains
  if render and args.raw:
    render_raw(out, sys_info)

  if json_mode:
    print(json.dumps(build_json(sys_info), indent=2, default=str))
  elif not args.quiet:
    out.out('')

  # Exit non-zero if the card fails any test: slower than rated (grade), smaller than reported (capacity), or an
  # impossible self-declaration in the CSD/CID (consistency)
  failed = False
  if not args.no_benchmark:
    failed = failed or not sys_info['grade']['pass']
  if 'capacity' in sys_info:
    failed = failed or not sys_info['capacity']['ok']
  if 'consistency' in sys_info:
    failed = failed or not sys_info['consistency']['ok']

  # Optional persist-to-SQLite. Runs after grading so pass/fail is known; a save failure warns but never changes
  # the exit code (the card verdict is what the exit code means, not whether the DB write worked)
  if args.save_db:
    status = errs if json_mode else progress
    try:
      saved = save_to_db(args.save_db, sys_info, not failed)
      status.out(status.badge('OK', 'pass') + ' Saved this run to ' + saved)
    except (sqlite3.Error, OSError) as error:
      errs.out(errs.badge('WARN', 'warn') + ' Could not save to the database ' + args.save_db + ': ' + str(error))

  return 1 if failed else 0

if __name__ == '__main__':
  sys.exit(main())
