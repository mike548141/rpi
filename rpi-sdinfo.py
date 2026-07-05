#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.5-20260705
# File:         rpi-sdinfo.py
# License:      GNU GPL v3
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
#   Performance testing is now native Python (see sdbench.py) - no external fio dependency. Nothing to install.
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
## Uses an assumption that the Linux kernel erase_size = block size. Does not yet handle erase_size / block size of 0 i.e. a SD that is not block-addressed
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

# Run external commands (dumpe2fs on Linux, diskutil on macOS)
import subprocess

# For the exit call
import sys

# Benchmark target directory default
import tempfile

# Native, dependency-free performance benchmark (replaces fio). Ships alongside this script
import sdbench

# Shared, dependency-free terminal styling (colour, sections, badges, spinner). Ships alongside this script
import ui

#======================================
# Declare the constants
#--------------------------------------

# Tool version and the version of the JSON document shape emitted by --format json. Bump SCHEMA only on a
# breaking change to the JSON structure so downstream consumers can rely on it
VERSION = '0.5-20260705'
SCHEMA = 'rpi-sdinfo/1'

# The default Linux device for the MMC or SD card (overridable with --device; the partition defaults to <device>p2)
block_device = 'mmcblk0'

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
  if isinstance(num_value, str):
    num_value = float(num_value)
  num_value = round(num_value, dec_places)
  return f"{num_value:n}"

def read_file(file_path, search_for='', return_scope='all', replace_with=''):
  # Returns '' (not None) when the file is absent so callers can safely concatenate, e.g. a Pi Zero has no eth0
  if os.path.isfile(file_path):
    file_contents = ''
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
      return file_contents
  return ''

def parse_kv(lines, separator=':'):
  # Parse 'key: value' style output (dumpe2fs, /proc/meminfo, ...) into a dict keyed by the label so we look
  # attributes up by name rather than by fragile line number / character offset
  result = {}
  for line in lines:
    if separator in line:
      key, _, value = line.partition(separator)
      result[key.strip()] = value.strip()
  return result

def mib(mem_value):
  # Convert a /proc/meminfo style 'N kB' value to MiB (its numeric leading field / 1024)
  return int(mem_value.split()[0]) / 1024

def safe_div(numerator, denominator):
  # Guard the disk-throughput maths against a divide-by-zero on a card that has been idle since boot
  return numerator / denominator if denominator else 0

def best_median(values, higher_is_better=True):
  # Real world runs are noisy, so drop the worst half (slow outliers, or high-latency outliers) and take the
  # median of what remains as a fair best-guess of the storage's rated performance
  ordered = sorted(values)
  half = math.floor(len(ordered) / 2)
  if higher_is_better:
    return statistics.median(ordered[half:])
  return statistics.median(ordered[:half] or ordered)

#======================================
# Gather - Linux (Raspberry Pi)
#--------------------------------------

def gather_linux(args):
  # Read everything the Linux kernel exposes about the Pi and its SD/MMC card, then derive the friendly fields.
  # sysfs paths are Linux-only; on any other platform gather_macos() is used instead.
  device = args.device or block_device
  partition = args.partition or (device + 'p2')

  # Load the source files once, up front, so the data is internally consistent and not read twice
  fs_info = parse_kv(subprocess.run(['/sbin/dumpe2fs', '-h', '/dev/' + partition], capture_output=True, encoding='utf-8', text=True, timeout=5).stdout.split('\n'))
  load_avg = read_file('/proc/loadavg').split()
  mem_info = parse_kv(read_file('/proc/meminfo').split('\n'))
  disk_stats = read_file('/proc/diskstats', ' ' + device + ' ', 'regex').split()
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

  # Analyse - capacity. Linux kernel dictates erase_size is 512 for a block-addressed card, 0 otherwise (see ROADMAP for the 0 case)
  block_size = sys_info['storage']['block_size'] or 512
  sys_info['storage']['bytes'] = sys_info['storage']['blocks'] * block_size
  sys_info['storage']['GB'] = sys_info['storage']['bytes'] / 1000000000
  sys_info['storage']['GiB'] = sys_info['storage']['bytes'] / 1024 / 1024 / 1024

  # Analyse - look up make, brand, model and rated speed class from the crowd-sourced CID database
  card_type, mid, oid, pnm, hwrev = (sys_info['storage'][k] for k in ('type', 'cid_mid', 'cid_oid', 'cid_pnm', 'cid_prv_hw'))
  try:
    sys_info['storage']['manufacturer'] = manufacturer[card_type][mid]['manufacturer']
  except KeyError:
    sys_info['storage']['manufacturer'] = 'unknown'
  try:
    sys_info['storage']['oem'] = manufacturer[card_type][mid][oid]['oem']
  except KeyError:
    sys_info['storage']['oem'] = sys_info['storage']['manufacturer']
  try:
    sys_info['storage']['label'] = manufacturer[card_type][mid][oid][pnm][hwrev]['label']
  except KeyError:
    sys_info['storage']['label'] = sys_info['storage']['oem']
  try:
    sys_info['storage']['speed_class'] = manufacturer[card_type][mid][oid][pnm][hwrev]['speed_class']
  except KeyError:
    sys_info['storage']['speed_class'] = []

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
  return sys_info

#======================================
# Gather - macOS
#--------------------------------------

def diskutil_info(path):
  # Return diskutil's info for a path or device as a dict, or {} on any failure. Accepts a mount path (e.g.
  # /Volumes/CARD) or a device id (e.g. disk4); macOS resolves either to the underlying whole disk
  try:
    output = subprocess.run(['diskutil', 'info', '-plist', path], capture_output=True, timeout=10).stdout
    return plistlib.loads(output)
  except (subprocess.SubprocessError, OSError, plistlib.InvalidFileException, ValueError):
    return {}

def _device_for_path(path):
  # Resolve the device that backs a directory path via df (diskutil info only accepts a mount point or device)
  try:
    lines = subprocess.run(['df', path], capture_output=True, encoding='utf-8', timeout=5).stdout.splitlines()
    return lines[1].split()[0] if len(lines) > 1 else ''
  except (subprocess.SubprocessError, OSError, IndexError):
    return ''

def gather_macos(args):
  # macOS cannot read the SD CID/CSD registers, so identity is limited to what the card reader reports
  target = args.device or args.dir or '/'
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
  # Query the Win32 API for a drive's volume label, filesystem and removable flag. Returns a dict; any field we
  # cannot read is simply omitted. Windows exposes no SD CID/CSD registers, so make/model stay unknown here too
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
  # Windows cannot read the SD CID/CSD registers, so identity is limited to the drive's capacity, volume label
  # and removable state. Resolve the target down to its drive root (e.g. 'E:\\') for the Win32 queries
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
  return sys_info

#======================================
# Report - print the gathered detail
#--------------------------------------

def render_report(console, sys_info):
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

def _render_linux_stats(console, sys_info):
  cpu = sys_info['stats']['cpu']
  memory = sys_info['stats']['memory']
  disk = sys_info['stats']['disk']
  device = sys_info['device']

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
# Performance test (native, see sdbench.py)
#--------------------------------------

def compute_perf(sys_info, args, spinner, progress):
  # Run the native benchmark, streaming per-run progress to `progress` (a Console), and stash the results plus
  # the best-half medians on sys_info. No grading here - see compute_grade()
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
  # The headline result table: best-half median plus mean and standard deviation over all runs
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
  # Compare the measured medians against the toughest target implied by the card's declared speed class(es),
  # falling back to A1 (the Raspberry Pi baseline) when no class is known. Returns a structured grade and stores
  # it on sys_info - no printing here, so it is reused by both the text and JSON renderers
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
# JSON (machine-readable) output
#--------------------------------------

def build_json(sys_info):
  # Assemble the machine-readable document in a stable key order. --format json emits exactly this on stdout so
  # other software and scripts can consume identity, benchmark samples, and the grade
  doc = {'schema': SCHEMA, 'tool_version': VERSION, 'generated': sys_info['generated']}
  for key in ('platform', 'device', 'partition', 'hardware', 'software', 'storage', 'filesystem', 'stats'):
    if key in sys_info:
      doc[key] = sys_info[key]
  if 'perf' in sys_info:
    doc['benchmark'] = sys_info['perf']
  if 'grade' in sys_info:
    doc['grade'] = sys_info['grade']
  return doc

#======================================
# Main
#--------------------------------------

def parse_args(argv=None):
  parser = argparse.ArgumentParser(description='Identify, benchmark, and grade an SD/MMC card (Raspberry Pi Linux, macOS, or Windows).')
  parser.add_argument('--device', help='Storage device to inspect. Linux: block device name (default: ' + block_device + '). macOS: disk id or mount path (e.g. disk4 or /Volumes/CARD). Windows: a drive (e.g. E:)')
  parser.add_argument('--partition', help='Linux filesystem partition to inspect (default: <device>p2)')
  parser.add_argument('--dir', help='Directory on the card to benchmark (default: /var/tmp on Linux, system temp dir on macOS/Windows). Point this at the mounted card, e.g. /Volumes/CARD or E:\\')
  parser.add_argument('--runs', type=int, default=max_runs, help='Number of benchmark runs to average (default: %(default)s)')
  parser.add_argument('--size-mb', type=int, default=sdbench.DEFAULT_SIZE_MB, help='Test file size in MiB (default: %(default)s)')
  parser.add_argument('--seconds', type=int, default=sdbench.DEFAULT_SECONDS, help='Duration of each random IO test (default: %(default)s)')
  parser.add_argument('--no-benchmark', action='store_true', help='Only gather and print card detail, skip the performance test')
  parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format (default: %(default)s). json emits the full result on stdout for other tools')
  parser.add_argument('--json', action='store_const', const='json', dest='format', help='Shortcut for --format json')
  parser.add_argument('--quiet', action='store_true', help='Suppress the report; exit code still reflects PASS/FAIL (handy in scripts)')
  color = parser.add_mutually_exclusive_group()
  color.add_argument('--color', dest='color', action='store_const', const=True, help='Force colour output (also: CLICOLOR_FORCE=1)')
  color.add_argument('--no-color', dest='color', action='store_const', const=False, help='Disable colour output (also: NO_COLOR=1)')
  parser.set_defaults(color=None)
  parser.add_argument('--version', action='version', version='rpi-sdinfo ' + VERSION)
  return parser.parse_args(argv)

def gather(args):
  # Dispatch to the right platform collector. Returns None on an unsupported platform
  if sys.platform == 'darwin':
    return gather_macos(args)
  if sys.platform.startswith('linux'):
    return gather_linux(args)
  if sys.platform == 'win32':
    return gather_windows(args)
  return None

def main(argv=None):
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

  sys_info = gather(args)
  if sys_info is None:
    errs.out(errs.badge('FAIL', 'fail') + ' Unsupported platform: ' + sys.platform
             + '. This tool supports Linux (Raspberry Pi), macOS, and Windows.')
    return 2
  sys_info['generated'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

  if not json_mode and not args.quiet:
    out.banner('rpi-sdinfo ' + VERSION, 'SD/MMC identity ' + out.g['dot'] + ' benchmark ' + out.g['dot'] + ' grade')
    render_report(out, sys_info)

  if not args.no_benchmark:
    try:
      compute_perf(sys_info, args, spinner, progress)
    except OSError as error:
      errs.out('')
      errs.out(errs.badge('FAIL', 'fail') + ' Could not benchmark ' + (args.dir or 'the default directory') + ': ' + str(error))
      return 2
    compute_grade(sys_info)

  if json_mode:
    print(json.dumps(build_json(sys_info), indent=2, default=str))
  elif not args.quiet:
    if not args.no_benchmark:
      render_benchmark(out, sys_info)
      render_grade(out, sys_info)
    out.out('')

  # Exit 0 when the card meets its rated performance (or no benchmark ran), 1 when it falls short
  if not args.no_benchmark:
    return 0 if sys_info['grade']['pass'] else 1
  return 0

if __name__ == '__main__':
  sys.exit(main())
