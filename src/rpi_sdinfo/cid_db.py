#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge  # leakscan:allow: standard per-file author header, matches cli.py
# File:         src/rpi_sdinfo/cid_db.py
# License:      Apache-2.0
# Language:     Python 3.6 or later
# Source:       https://github.com/mike548141/rpi
#
# Description:
#   The crowd-sourced CID identity database and its structural validator, split out of cli.py so it can grow
#   as its own file: a contribution is a diff against this table (data), not against the tool (code), and it
#   gives a future shared/uploadable database one place to serialise from. Every leaf carries its source CID in
#   a trailing `# CID:...` comment - that provenance is the whole point, so a new entry without a real observed
#   CID behind it does not belong here (an invented mapping poisons fake-detection rather than strengthening it).
#
#   Structure: manufacturer[card_type][MID]['manufacturer'] is the make; an optional [OID]['oem'] narrows the
#   brand; an optional [PNM][PRV] leaf is a fully-identified product carrying 'label' (and optionally
#   'speed_class' / 'alternate'). _lookup() in cli.py walks it, returning a default the moment a level is
#   missing, so a partial entry degrades gracefully.

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


# Structural token shapes. The CID fields are fixed-width hex the kernel formats predictably (see gather_linux),
# so a key that does not match is a data-entry slip, not a card we have never seen.
import re as _re

_MID_RE = _re.compile(r'^0x[0-9a-f]{6}$')      # manfid: 8-bit id, but sysfs zero-pads to 6 hex digits
_OID_RE = _re.compile(r'^0x[0-9a-f]{4}$')      # oemid: 2 ASCII chars rendered as 4 hex digits
_PRV_RE = _re.compile(r'^0x[0-9a-f]+$')        # hwrev nibble, e.g. 0x8
_LABEL_GB_RE = _re.compile(r'(\d+)\s*GB\b', _re.IGNORECASE)

_LEAF_KEYS = ('label', 'alternate', 'speed_class', 'capacity_bytes')


def leaf_capacity_bytes(label):
  """Best-effort machine-readable capacity from a product label ('... 64 GB ...' -> 64000000000).

  The label is the single source of truth - we never store a separate, drift-prone capacity field. Marketing GB
  is 10^9 bytes (the convention this tool prints in). Returns None when the label states no parseable GB size, so
  a caller simply does not run the capacity cross-check rather than guessing.
  """
  if not label:
    return None
  m = _LABEL_GB_RE.search(label)
  if not m:
    return None
  return int(m.group(1)) * 1000 ** 3


def validate_cid_db(tree=None, known_speed_classes=None):
  """Structurally validate the CID database, returning a list of human-readable problem strings (empty == clean).

  Pure and dependency-free so CI can gate every contribution as the table grows: it catches malformed MID/OID/PRV
  keys, leaf entries with no identifying label, unknown speed-class tokens (when the caller supplies the known
  set), and a label whose stated GB size disagrees with an explicit capacity_bytes. It deliberately does NOT
  judge whether a mapping is *true* - only that it is well-formed; provenance stays a human-review concern.
  """
  if tree is None:
    tree = manufacturer
  problems = []

  def is_leaf(node):
    return isinstance(node, dict) and any(k in node for k in _LEAF_KEYS)

  def walk_prv(where, prv_node):
    if not isinstance(prv_node, dict):
      problems.append('%s: expected a dict of hwrev -> product, got %r' % (where, type(prv_node).__name__))
      return
    for prv, leaf in prv_node.items():
      at = '%s/%s' % (where, prv)
      if not _PRV_RE.match(str(prv)):
        problems.append('%s: hwrev key %r is not lowercase hex like 0x8' % (at, prv))
      if not isinstance(leaf, dict):
        problems.append('%s: leaf is not a dict' % at)
        continue
      if not (leaf.get('label') or leaf.get('alternate')):
        problems.append('%s: product leaf has neither label nor alternate' % at)
      sc = leaf.get('speed_class')
      if sc is not None:
        if not isinstance(sc, list):
          problems.append('%s: speed_class must be a list, got %r' % (at, type(sc).__name__))
        elif known_speed_classes is not None:
          for tok in sc:
            if tok not in known_speed_classes:
              problems.append('%s: unknown speed_class token %r' % (at, tok))
      cap = leaf.get('capacity_bytes')
      if cap is not None:
        from_label = leaf_capacity_bytes(leaf.get('label'))
        if from_label is not None and from_label != cap:
          problems.append('%s: capacity_bytes %r disagrees with the label size %r' % (at, cap, from_label))

  for card_type, mids in (tree or {}).items():
    if card_type not in ('SD', 'MMC'):
      problems.append('top-level key %r is not SD or MMC' % card_type)
    if not isinstance(mids, dict):
      problems.append('%s: expected a dict of MID -> entry' % card_type)
      continue
    for mid, entry in mids.items():
      at = '%s/%s' % (card_type, mid)
      if not _MID_RE.match(str(mid)):
        problems.append('%s: MID key is not zero-padded lowercase hex like 0x000003' % at)
      if not isinstance(entry, dict):
        problems.append('%s: MID entry is not a dict' % at)
        continue
      for key, node in entry.items():
        if key == 'manufacturer':
          if not isinstance(node, str) or not node:
            problems.append('%s: manufacturer must be a non-empty string' % at)
          continue
        oat = '%s/%s' % (at, key)
        if not _OID_RE.match(str(key)):
          problems.append('%s: OID key is not hex like 0x5344 (or an unexpected field)' % oat)
          continue
        if not isinstance(node, dict):
          problems.append('%s: OID entry is not a dict' % oat)
          continue
        for pk, pnode in node.items():
          if pk == 'oem':
            if not isinstance(pnode, str) or not pnode:
              problems.append('%s: oem must be a non-empty string' % oat)
            continue
          # anything else under an OID is a product-name node mapping PRV -> leaf
          walk_prv('%s/%s' % (oat, pk), pnode)

  return problems
