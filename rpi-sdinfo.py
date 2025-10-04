#!/usr/bin/python
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.2-20231020
# File:         rpi-sdinfo.py
# License:      GNU GPL v3
# Language:     Python 3.6 or later
# Source:       https://github.com/mike548141/sdinfo/
#
# Description:
#   Performance test SD cards and MMC, and try (perhaps in vain) to help people to spot fake MMC/SD cards by comapring the cards registers to it branding.
#   I'm using gigabyte (GB) for storage and mebibyte (MiB) for memory because thats what I see they industry typically using in product branding and marketing
#
# Pre-requisite:
#   Designed and tested on a Raspberry Pi 3 Model B Rev 1.2 and a Raspberry Pi Zero W Rev 1.1, both running Raspberry Pi OS Lite 12 (bookworm).
#   Requires the fio package be installed for performance testing of the SD card.
#
# References:
#
# Inputs (parameters):
#
# Outputs:
#

# Issues:
## fio had a faux pas sometime ago where it confused Base-10 and Base-2 (e.g. MB and MiB). So I'm not sure what units we are getting from fio here but I'm assuming Base-10
## I can't get f strings to work with both localisation and a max number of decimal places. Using a function as a work around
## Option to save to SQLite DB and/or JSON file
## Option for raw output of all relevant detail e.g. all of dumpe2fs etc
## I would like to select lines from meminfo and dumpe2fs using attribute titles (regex) instead of line number
## Option to post to a API or S3 bucket so everyone can share results and build a database of MMC & SD card identifiers (CID). Maybe CSD too
## Uses an assumption that the Linux kernel erase_size = block size. Handle if erase_size / block size is 0 i.e. a SD is not block-addressed
## Improve the exception handling
## Make read_file able to return multiple lines specified by line numbers, not just a single. And test regex returns multiple lines incl

#======================================
# Import the libraries
#--------------------------------------

# Package manager
import apt

# Time delta
import datetime

# Hash encoding
import hashlib

# JSON handler
import json

# Locale relevant feedback
import locale

#
import math

# Read files
import os

# Platform info like OS kernel
import platform

# Regular expression matching
import re

# Advanced math
import statistics

# Run external commands
import subprocess

# For the exit call
import sys

#======================================
# Declare the constants
#--------------------------------------

# The Linux device for the MMC or SD card
block_device = 'mmcblk0'
block_partition = 'mmcblk0p2'

# The total number of performance tests to run to ensure a consistent result
max_runs = 6
# Number of jobs per performance test
max_jobs = 4
# File used for performance testing
test_file = '/var/tmp/sd.test.file'

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

#======================================
# Execute the script
#--------------------------------------

# Loading the files here instead of in sys_info to save reading the same file multiple times and ensure the data read is consistent i.e. doesn't change between reads
# Filesystem info
fs_info = subprocess.run(['/sbin/dumpe2fs', '-h', '/dev/' + block_partition], capture_output=True, encoding='utf-8', text=True, timeout=3).stdout.split('\n')
# CPU load averages
load_avg = read_file('/proc/loadavg').split()
# Memory utilisation info
mem_info = read_file('/proc/meminfo').split('\n')
# Disk statistics for the MMC/SD card
disk_stats = read_file('/proc/diskstats', ' ' + block_device + ' ', 'regex').split()
# Salt
salt = os.urandom(32)

sys_info = {
  'hardware' : {
    'model' : read_file('/sys/firmware/devicetree/base/model', '\x00'),
    'serial_number' : read_file('/sys/firmware/devicetree/base/serial-number', '\x00'),
    'uuid' : hashlib.pbkdf2_hmac('sha256', read_file('/sys/firmware/devicetree/base/serial-number', '\x00').encode('utf-8'), salt, 1000).hex(),
    'mac_eth0' : read_file('/sys/class/net/eth0/address', '\n'),
    'mac_wlan0' : read_file('/sys/class/net/wlan0/address', '\n'),
    'mac_bt0' : read_file('/sys/kernel/debug/bluetooth/hci0/identity')[0:17]
  },
  'software' : {
    'os_release' : platform.freedesktop_os_release().get('PRETTY_NAME', 'Linux'),
    'os_kernel' : platform.release()
  },
  'storage' : {
    'type' : read_file('/sys/block/' + block_device + '/device/type', '\n'),
    'read_only' : read_file('/sys/block/' + block_device + '/ro', '\n'),                   # Hardware boolean to force read only, on SD cards thats controlled by a switch on its side
    'force_read_only' : read_file('/sys/block/' + block_device + '/force_ro', '\n'),       # Software boolean to force read only
    'removable' : read_file('/sys/block/' + block_device + '/removable', '\n'),
    'blocks' : int(read_file('/sys/block/' + block_device + '/size', '\n')),
    'block_size' : int(read_file('/sys/block/' + block_device + '/device/erase_size', '\n')),
    'ocr' : read_file('/sys/block/' + block_device + '/device/ocr', '\n'),                 # Operation Conditions Register
    'cid' : read_file('/sys/block/' + block_device + '/device/cid', '\n'),                 # Card Identification register is 16 bytes (128 bits) code that contains information that uniquely identifies the MMC/SD card
    'cid_mid' : read_file('/sys/block/' + block_device + '/device/manfid', '\n'),          # Manufacturer ID (from CID Register). 8-bit number that identifies the manufacturer, assigned by SD-3C
    'cid_oid' : read_file('/sys/block/' + block_device + '/device/oemid', '\n'),           # OEM/Application ID (from CID Register). 2-character ASCII string that identifies the card OEM and/or the card contents, assigned by SD-3C
    'cid_pnm' : read_file('/sys/block/' + block_device + '/device/name', '\n'),            # Product Name (from CID Register). 5-character ASCII string
    'cid_prv_hw' : read_file('/sys/block/' + block_device + '/device/hwrev', '\n'),        # Hardware/Product Revision (from CID Register) (SD and MMCv1 only). PRV is composed of two Binary Coded Decimal (BCD) digits, four bits each, representing an “n.m” revision number
    'cid_prv_fw' : read_file('/sys/block/' + block_device + '/device/fwrev', '\n'),        # Firmware/Product Revision (from CID Register) (SD and MMCv1 only). PRV is composed of two Binary Coded Decimal (BCD) digits, four bits each, representing an “n.m” revision number
    'cid_psn' : read_file('/sys/block/' + block_device + '/device/serial', '\n'),          # Product serial number is 32 bits ordinary number
    'cid_mdt' : read_file('/sys/block/' + block_device + '/device/date', '\n'),            # Manufacturing Date (from CID Register), composed of 12 bits in YYM format, (offset from 2000)
    'csd' : read_file('/sys/block/' + block_device + '/device/csd', '\n'),                 # Card Specific Data register
    'rca' : read_file('/sys/block/' + block_device + '/device/rca', '\n'),                 # Relative Card Address register
    'dsr' : read_file('/sys/block/' + block_device + '/device/dsr', '\n'),                 # Driver Stage Register
    'scr' : read_file('/sys/block/' + block_device + '/device/scr', '\n'),                 # SD Card Configuration Register (SD only)
    'ssr' : read_file('/sys/block/' + block_device + '/device/ssr', '\n')                  # SD Status Register
  },
  'filesystem' : {
    'state' : fs_info[8].split()[2],
    'created' : fs_info[25][26:50],
    'last_checked' : fs_info[30][26:50],
    'mount_count' : int(fs_info[28].split()[2]),
    'last_mount' : fs_info[26][26:50]
  },
  'stats' : {
    'cpu' : {
      'load_1m' : float(load_avg[0]),
      'load_5m' : float(load_avg[1]),
      'load_15m' : float(load_avg[2]),
      'threads' : load_avg[3]
    },
    'memory' : {
      'total' : int(mem_info[0].split()[1]) / 1024,
      'free' : int(mem_info[1].split()[1]) / 1024,
      'available' : int(mem_info[2].split()[1]) / 1024,
      'buffers' : int(mem_info[3].split()[1]) / 1024,
      'cached' : int(mem_info[4].split()[1]) / 1024,
      'swap_total' : int(mem_info[14].split()[1]) / 1024,
      'swap_free' : int(mem_info[15].split()[1]) / 1024,
      'vm_alloc_total' : int(mem_info[35].split()[1]) / 1024,
      'vm_alloc_used' : int(mem_info[36].split()[1]) / 1024
    },
    'disk' : {
      'major_number' : int(disk_stats[0]),
      'minor_number' : int(disk_stats[1]),
      'read_completed' : int(disk_stats[3]),
      'read_merged' : int(disk_stats[4]),
      'read_sectors' : int(disk_stats[5]),
      'read_time' : int(disk_stats[6]),
      'write_completed' : int(disk_stats[7]),
      'write_merged' : int(disk_stats[8]),
      'write_sectors' : int(disk_stats[9]),
      'write_time' : int(disk_stats[10]),
      'io_in_progress' : int(disk_stats[11]),
      'io_time' : int(disk_stats[12]),
      'io_weighted_time' : int(disk_stats[13]),
      'discard_completed' : int(disk_stats[14]),
      'discard_merged' : int(disk_stats[15]),
      'discard_sectors' : int(disk_stats[16]),
      'discard_time' : int(disk_stats[17]),
      'flush_completed' : int(disk_stats[18]),
      'flush_time' : int(disk_stats[19])
    }
  },
  'fio' : {
    'write' : {
      'seq_mbps' : [],
      'seq_iops' : [],
      'seq_latency' : [],
      'rand_4kb_mbps' : [],
      'rand_4kb_iops' : [],
      'rand_4kb_latency' : []
    },
    'read' : {
      'rand_4kb_mbps' : [],
      'rand_4kb_iops' : [],
      'rand_4kb_latency' : []
    }
  }
}

## Linux kernel dictates that for SD, erase_size is 512 if the card is block-addressed, 0 otherwise. This does not handle a zero value
sys_info['storage']['bytes'] = sys_info['storage']['blocks'] * sys_info['storage']['block_size']
sys_info['storage']['GB'] = sys_info['storage']['bytes'] / 1000000000
sys_info['storage']['GiB'] = sys_info['storage']['bytes'] / 1024 / 1024 / 1024

# Look up the make and model of storage
try:
  sys_info['storage']['manufacturer'] = manufacturer[sys_info['storage']['type']][sys_info['storage']['cid_mid']]['manufacturer']
except KeyError:
  sys_info['storage']['manufacturer'] = 'unknown'

try:
  sys_info['storage']['oem'] = manufacturer[sys_info['storage']['type']][sys_info['storage']['cid_mid']][sys_info['storage']['cid_oid']]['oem']
except KeyError:
  sys_info['storage']['oem'] = sys_info['storage']['manufacturer']

try:
  sys_info['storage']['label'] = manufacturer[sys_info['storage']['type']][sys_info['storage']['cid_mid']][sys_info['storage']['cid_oid']][sys_info['storage']['cid_pnm']][sys_info['storage']['cid_prv_hw']]['label']
except KeyError:
  sys_info['storage']['label'] = sys_info['storage']['oem']

# Card state
if ((sys_info['storage']['read_only'] == '0') and (sys_info['storage']['force_read_only'] == '0')):
  sys_info['storage']['state'] = 'read/write'
elif ((sys_info['storage']['read_only'] == '1') and (sys_info['storage']['force_read_only'] == '1')):
  sys_info['storage']['state'] = 'read only (hardware+software)'
elif (sys_info['storage']['read_only'] == '1'):
  sys_info['storage']['state'] = 'read only (hardware)'
elif (sys_info['storage']['force_read_only'] == '1'):
  sys_info['storage']['state'] = 'read only (software)'

if (sys_info['storage']['removable'] == '1'):
  sys_info['storage']['removable_label'] = 'removable'
elif (sys_info['storage']['removable'] == '0'):
  sys_info['storage']['removable_label'] = 'not removable'

# Look for a recent history of high CPU utilisation that may affect performance testing
if ((sys_info['stats']['cpu']['load_1m'] >= 1.0) or ((sys_info['stats']['cpu']['load_1m'] >= 0.5) and (sys_info['stats']['cpu']['load_5m'] >= 0.7) and (sys_info['stats']['cpu']['load_15m'] >= 0.7))):
  sys_info['stats']['cpu']['warning'] = '    Warning high CPU load!!'
else:
  sys_info['stats']['cpu']['warning'] = ''

# Analyse the disk stats for real world throughput and IO per second
sys_info['stats']['disk']['read_avg_mbps'] = ((sys_info['stats']['disk']['read_sectors'] * sys_info['storage']['block_size']) / 1000000) / (sys_info['stats']['disk']['read_time'] / 1000)
sys_info['stats']['disk']['read_avg_mibps'] = ((sys_info['stats']['disk']['read_sectors'] * sys_info['storage']['block_size']) / 1024 / 1024) / (sys_info['stats']['disk']['read_time'] / 1000)
sys_info['stats']['disk']['read_avg_iops'] = sys_info['stats']['disk']['read_completed'] / (sys_info['stats']['disk']['read_time'] / 1000)
sys_info['stats']['disk']['write_avg_mbps'] = ((sys_info['stats']['disk']['write_sectors'] * sys_info['storage']['block_size']) / 1000000) / (sys_info['stats']['disk']['write_time'] / 1000)
sys_info['stats']['disk']['write_avg_mibps'] = ((sys_info['stats']['disk']['write_sectors'] * sys_info['storage']['block_size']) / 1024 / 1024) / (sys_info['stats']['disk']['write_time'] / 1000)
sys_info['stats']['disk']['write_avg_iops'] = sys_info['stats']['disk']['write_completed'] / (sys_info['stats']['disk']['write_time'] / 1000)

# System info
print('\n' + sys_info['hardware']['model'] + ' (serial: ' + sys_info['hardware']['serial_number'] + ')\n   Has been up for ' + str(datetime.timedelta(seconds = float(read_file('/proc/uptime', '\n').split()[0]))) + ' running ' + sys_info['software']['os_release'] + ' with kernel ' + sys_info['software']['os_kernel'])
print('   Ethernet MAC:  ' + sys_info['hardware']['mac_eth0'] + '\n   WiFi MAC:      ' + sys_info['hardware']['mac_wlan0'] + '\n   Bluetooth MAC: ' + sys_info['hardware']['mac_bt0'])
# Storage info
print('\nThe ' + sys_info['storage']['type'] + ' storage is a ' + sys_info['storage']['label'])
print('   Capacity reported:           ' + f_num(sys_info['storage']['GB'], 1) + ' GB (' + f_num(sys_info['storage']['GiB'], 1) + ' GiB, ' + f_num(sys_info['storage']['blocks']) + ' blocks of ' + f_num(sys_info['storage']['block_size']) + ' bytes)\n   Manufacturers serial number: ' + sys_info['storage']['cid_psn'] + '\n   Manufacture date (mm/yyyy):  ' + sys_info['storage']['cid_mdt'])
print('   The ' + sys_info['storage']['manufacturer'] + ' storage controller is running firmware revision ' + sys_info['storage']['cid_prv_fw'] + '\n   The card is ' + sys_info['storage']['state'] + ' and is ' + sys_info['storage']['removable_label'])
print('\n' + sys_info['storage']['type'] + ' Registers:\n   OCR: ' + sys_info['storage']['ocr'] + '\n   CID: ' + sys_info['storage']['cid'] + '\n   CSD: ' + sys_info['storage']['csd'] + '\n   RCA: ' + sys_info['storage']['rca'] + '\n   DSR: ' + sys_info['storage']['dsr'] + '\n   SCR: ' + sys_info['storage']['scr'] + '\n   SSR: ' + sys_info['storage']['ssr'])
print('\nThe Filesystem of ' + block_partition + ' is ' + sys_info['filesystem']['state'] + '\n   Created:      ' + sys_info['filesystem']['created'] + '\n   Last checked: ' + sys_info['filesystem']['last_checked'] + '\n   Mounted:      ' + f_num(sys_info['filesystem']['mount_count']) + ' times since the filesystem was created\n   Last mounted: ' + sys_info['filesystem']['last_mount'])
# System load info
print('\n CPU load average (1m): ' + f_num(sys_info['stats']['cpu']['load_1m'], 2) + sys_info['stats']['cpu']['warning'] + '\n                  (5m): ' + f_num(sys_info['stats']['cpu']['load_5m'], 2) + '\n                 (15m): ' + f_num(sys_info['stats']['cpu']['load_15m'], 2) + '\nThreads (active/total): ' + sys_info['stats']['cpu']['threads'])
print('                Memory: ' + f_num(sys_info['stats']['memory']['free']) + ' MiB free of ' + f_num(sys_info['stats']['memory']['total']) + ' MiB total\n                  Swap: ' + f_num(sys_info['stats']['memory']['swap_free']) + ' MiB free of ' + f_num(sys_info['stats']['memory']['swap_total']) + ' MiB total')
print(' Storage ' + block_device + ' reads: ' + f_num(sys_info['stats']['disk']['read_completed']) + ' from ' + f_num(sys_info['stats']['disk']['read_sectors']) + ' sectors in ' + f_num(sys_info['stats']['disk']['read_time']) + ' ms\n                        ' + f_num(sys_info['stats']['disk']['read_avg_mbps'], 1) + ' MBps (' + f_num(sys_info['stats']['disk']['read_avg_mibps'], 1) + ' MiBps) using ' + f_num(sys_info['stats']['disk']['read_avg_iops']) + ' IOPS\n                writes: ' + f_num(sys_info['stats']['disk']['write_completed']) + ' to ' + f_num(sys_info['stats']['disk']['write_sectors']) + ' sectors in ' + f_num(sys_info['stats']['disk']['write_time']) + ' ms\n                        ' + f_num(sys_info['stats']['disk']['write_avg_mbps'], 1) + ' MBps (' + f_num(sys_info['stats']['disk']['write_avg_mibps'], 1) + ' MiBps) using ' + f_num(sys_info['stats']['disk']['write_avg_iops']) + ' IOPS\n              discards: ' + f_num(sys_info['stats']['disk']['discard_completed']) + ' from ' + f_num(sys_info['stats']['disk']['discard_sectors']) + ' sectors in ' + f_num(sys_info['stats']['disk']['discard_time']) + ' ms\n               flushes: ' + f_num(sys_info['stats']['disk']['flush_completed']) + ' in ' + f_num(sys_info['stats']['disk']['flush_time']) + ' ms\n            Active I/O: ' + f_num(sys_info['stats']['disk']['io_in_progress']) + ' in ' + f_num(sys_info['stats']['disk']['io_time']) + ' ms (weighted ' + f_num(sys_info['stats']['disk']['io_weighted_time']) + ' ms)')

# Ensure fio is installed for storage speed testing
cache = apt.Cache()
try:
  if cache['fio'].is_installed:
    print('\nPerformance testing ' + block_device + ', this is non-destructive so it will not mess with your data. This does create a test file (' + test_file + ') which will be removed after the tests are completed')
except KeyError:
  print('\n\nYou need to install fio to run performance testing on your ' + sys_info['storage']['type'] + ' storage\nsudo apt -y install fio\n\n')
  exit(1)

# Create fio job file with job details
if os.path.isfile('/usr/share/fio/sd_bench.fio') == False:
  with open('/usr/share/fio/sd_bench.fio', 'w') as file_pointer:
    file_pointer.write('# Use FIO to emulate the Apps Class A1 performance test.\n# This is not an exact benchmark as the card is not in the state required by the\n# specification, but is good enough as a sniff test.\n#\n[global]\nioengine=libaio\niodepth=4\nsize=64m\ndirect=1\nend_fsync=1\ndirectory=' + os.path.split(test_file)[0] + '\nfilename=' + os.path.split(test_file)[1] + '\n\n[prepare-file]\nrw=write\nbs=512k\nstonewall\n\n[seq-write]\nrw=write\nbs=512k\nstonewall\n\n[rand-4k-write]\nrw=randwrite\nbs=4k\nruntime=10\nstonewall\n\n[rand-4k-read]\nrw=randread\nbs=4k\nruntime=10\nstonewall\n\n# execute with command $ fio --output-format=terse sd_bench.fio | cut -f 3,7,8,48,49 -d";" -\n# testname, read bandwidth, read iops, write bandwidth, write iops')

# Run performance testing
for run in range(1, max_runs + 1):
  fio_results = json.loads(subprocess.run(['/usr/bin/fio', '--output-format=json', '--max-jobs=' + max_jobs, '/usr/share/fio/sd_bench.fio'], capture_output=True, encoding='utf-8', text=True, timeout=90).stdout)
  ## Not sure if fio is reporting bw, random reads & writes in KB or KiB
  for job in range(1, max_jobs):
    if fio_results['jobs'][job]['jobname'] == 'seq-write':
      sys_info['fio']['write']['seq_mbps'].append(fio_results['jobs'][job]['write']['bw'] / 1000)
      sys_info['fio']['write']['seq_iops'].append(fio_results['jobs'][job]['write']['iops'])
      sys_info['fio']['write']['seq_latency'].append(fio_results['jobs'][job]['write']['lat_ns']['mean'] / 1000000)
    elif fio_results['jobs'][job]['jobname'] == 'rand-4k-write':
      sys_info['fio']['write']['rand_4kb_mbps'].append(fio_results['jobs'][job]['write']['bw'] / 1000)
      sys_info['fio']['write']['rand_4kb_iops'].append(fio_results['jobs'][job]['write']['iops'])
      sys_info['fio']['write']['rand_4kb_latency'].append(fio_results['jobs'][job]['write']['lat_ns']['mean'] / 1000000)
    elif fio_results['jobs'][job]['jobname'] == 'rand-4k-read':
      sys_info['fio']['read']['rand_4kb_mbps'].append(fio_results['jobs'][job]['read']['bw'] / 1000)
      sys_info['fio']['read']['rand_4kb_iops'].append(fio_results['jobs'][job]['read']['iops'])
      sys_info['fio']['read']['rand_4kb_latency'].append(fio_results['jobs'][job]['read']['lat_ns']['mean'] / 1000000)
  
  print('   Run ' + str(run) + ' of ' + str(max_runs) + ': ' + f_num(sys_info['fio']['write']['seq_mbps'][run], 1) + ' MBps, ' + f_num(sys_info['fio']['write']['seq_iops'][run]) + ' IOPS, ' + f_num(sys_info['fio']['write']['seq_latency'][run]) + ' ms    ' + f_num(sys_info['fio']['write']['rand_4kb_mbps'][run], 1) + ' MBps, ' + f_num(sys_info['fio']['write']['rand_4kb_iops'][run]) + ' IOPS, ' + f_num(sys_info['fio']['write']['rand_4kb_latency'][run]) + ' ms    ' + f_num(sys_info['fio']['read']['rand_4kb_mbps'][run], 1) + ' MBps, ' + f_num(sys_info['fio']['read']['rand_4kb_iops'][run]) + ' IOPS, ' + f_num(sys_info['fio']['read']['rand_4kb_latency'][run]) + ' ms')

print('                   Sequential Writes            Random 4 KB writes            Random 4 KB reads')

if os.path.isfile(test_file):
  os.remove(test_file)

# Somethimes thing will negatively affect the performance results so we take the median of the best results as a best guess of the real world performance while still being applicable to the storages rated speed
# Get the median of the upper half of the MBps and IOPS results and the lower half of the latency
sys_info['fio']['write']['seq_mbps_result'] = statistics.median(sorted(sys_info['fio']['write']['seq_mbps'])[(math.floor(len(sys_info['fio']['write']['seq_mbps']) / 2)):len(sys_info['fio']['write']['seq_mbps'])])
sys_info['fio']['write']['seq_iops_result'] = statistics.median(sorted(sys_info['fio']['write']['seq_iops'])[(math.floor(len(sys_info['fio']['write']['seq_iops']) / 2)):len(sys_info['fio']['write']['seq_iops'])])
sys_info['fio']['write']['seq_latency_result'] = statistics.median(sorted(sys_info['fio']['write']['seq_latency'])[0:(math.floor(len(sys_info['fio']['write']['seq_latency']) / 2))])


print('\nAverage of the results from ' + str(max_runs) + ' runs\n   Sequential Writes:  ' + f_num(statistics.mean(sys_info['fio']['write']['seq_mbps']), 1) + ' MBps (stdev ' + f_num(statistics.stdev(sys_info['fio']['write']['seq_mbps']), 1) + ')\n                       ' + f_num(statistics.mean(sys_info['fio']['write']['seq_iops'])) + ' IOPS (stdev ' + f_num(statistics.stdev(sys_info['fio']['write']['seq_iops']), 1) + ')\n                       ' + f_num(statistics.mean(sys_info['fio']['write']['seq_latency'])) + ' ms (stdev ' + f_num(statistics.stdev(sys_info['fio']['write']['seq_latency']), 1) + ')')
print('\n   Random 4 KB Writes: ' + f_num(statistics.mean(sys_info['fio']['write']['rand_4kb_mbps']), 1) + ' MBps (stdev ' + f_num(statistics.stdev(sys_info['fio']['write']['rand_4kb_mbps']), 1) + ')\n                       ' + f_num(statistics.mean(sys_info['fio']['write']['rand_4kb_iops'])) + ' IOPS (stdev ' + f_num(statistics.stdev(sys_info['fio']['write']['rand_4kb_iops']), 1) + ')\n                       ' + f_num(statistics.mean(sys_info['fio']['write']['rand_4kb_latency'])) + ' ms (stdev ' + f_num(statistics.stdev(sys_info['fio']['write']['rand_4kb_latency']), 1) + ')')
print('\n   Random 4 KB Reads:  ' + f_num(statistics.mean(sys_info['fio']['read']['rand_4kb_mbps']), 1) + ' MBps (stdev ' + f_num(statistics.stdev(sys_info['fio']['read']['rand_4kb_mbps']), 1) + ')\n                       ' + f_num(statistics.mean(sys_info['fio']['read']['rand_4kb_iops'])) + ' IOPS (stdev ' + f_num(statistics.stdev(sys_info['fio']['read']['rand_4kb_iops']), 1) + ')\n                       ' + f_num(statistics.mean(sys_info['fio']['read']['rand_4kb_latency'])) + ' ms (stdev ' + f_num(statistics.stdev(sys_info['fio']['read']['rand_4kb_latency']), 1) + ')')



### Finish removing _list and [run]. Ammend structure too ['fio']['read'] and write






# Summary:
## Take median of the top half of results. Base the standard deviation on the whole list. Do that for mbps, iops, and latency
## Handle no eth0 eg on RPi Zero
# Lookup what speed class (eg A1) the card should be, A1 if can't find
## Show results against expected card spec or A1 as fallback - MiB & IOps seq wr 10 MBps, rand read 1500 IOps, rand write 500 IOps
# Message to user if below spec: Note that sequential write speed declines over time as a card is used - your card may require reformatting

#======================================
# Event handlers & timer loop
#--------------------------------------

#======================================
# Exit the script
#--------------------------------------
