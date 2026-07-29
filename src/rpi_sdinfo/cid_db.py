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
import re as _re  # noqa: E402  (kept beside the validator it serves, not hoisted away from its explanation)

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


#======================================
# Brand-set signal (learned, never a verdict)
#--------------------------------------
#
# ADR 0007's addendum: the naive "brand != MID => fake" trigger is unsound (OEM/ODM rebadging means a genuine card
# legitimately carries another maker's MID - the DB's own Phison -> Sony/Lexar/PNY OEM line proves it), but the
# brand<->MID *relationship* is real, learnable data. So the free-text make/OEM brand lists already in the table
# are folded into a countable set of brands observed shipping under each MID (and, where an OEM line narrows it,
# each MID/OID). Derived live from `manufacturer` below, so the set grows with the table - there is no parallel
# hand-maintained list to drift out of sync. This first slice feeds only a neutral *info* context (cli.cross_check):
# an unseen pairing produces nothing and reads neutral, never a suspicion signal. The aggregate suspicion score is
# a later slice with its own ADR.

# A curated make/OEM field is a comma / "or"-delimited list of brand names ("AgfaPhoto, Delkin, ... or Verbatim",
# "Kingston, Toshiba, or Viking"). Split on either token; \b anchors keep "or" from matching inside a name
# (Corsair, Polaroid). A parenthetical grade qualifier is stripped so a brand collapses across variants
# ("Angelbird (V60)" and "Angelbird (V90)" -> one "Angelbird").
_BRAND_SPLIT_RE = _re.compile(r',|\bor\b', _re.IGNORECASE)
_PAREN_RE = _re.compile(r'\s*\([^)]*\)')

# A separator or bracket surviving in a token means the parse leaked; used by the validator to catch a regression.
_BRAND_LEAK_RE = _re.compile(r',|\bor\b', _re.IGNORECASE)

# Non-brand placeholders that sit in the make/OEM fields as "we don't know" rather than a real brand. They must
# never enter a brand set - an unknown maker is not a brand literally called "Unknown".
_NON_BRANDS = frozenset(('unknown', ''))


def brands_from_field(text):
  """Parse one free-text make/OEM field into a sorted list of distinct brand names ([] when it names none).

  Only the make and OEM fields are parsed for brands: they are curated, delimited brand lists. Product *labels*
  are prose ('SanDisk Ultra 64 GB microSDXC U1') where the brand boundary is a guess, so they are deliberately
  NOT mined here - inventing a "brand" out of a label fragment would poison the very signal this feeds, against
  the honesty floor (never invent brand data; ADR 0007). Placeholders like 'Unknown' are dropped.
  """
  if not text:
    return []
  seen = []
  for part in _BRAND_SPLIT_RE.split(text):
    brand = _PAREN_RE.sub('', part).strip()
    if brand.lower() in _NON_BRANDS:
      continue
    if brand not in seen:
      seen.append(brand)
  return sorted(seen)


def brand_sets(tree=None):
  """Derive the brand-set model from the CID table: {card_type: {MID: {'brands': [...], 'by_oid': {OID: [...]}}}}.

  Per MID, 'brands' is the union of every brand named in that MID's make field and in every OEM line beneath it -
  the full set of brands observed shipping under that maker id. 'by_oid' keeps the per-OEM-line sets for the finer
  MID/OID granularity a later scored signal will want. A MID that names no brand (an unknown maker, a product-only
  entry with no OEM string) yields an empty set and simply does not appear: an absent pairing is neutral, never
  suspicious (ADR 0004 / ADR 0007). Derived, not maintained, so it tracks the table automatically.
  """
  if tree is None:
    tree = manufacturer
  model = {}
  for card_type, mids in (tree or {}).items():
    if not isinstance(mids, dict):
      continue
    for mid, entry in mids.items():
      if not isinstance(entry, dict):
        continue
      brands = set(brands_from_field(entry.get('manufacturer', '')))
      by_oid = {}
      for key, node in entry.items():
        if key == 'manufacturer' or not isinstance(node, dict):
          continue
        oid_brands = brands_from_field(node.get('oem', ''))
        if oid_brands:
          by_oid[key] = oid_brands
          brands.update(oid_brands)
      if brands:
        model.setdefault(card_type, {})[mid] = {'brands': sorted(brands), 'by_oid': by_oid}
  return model


_BRAND_SETS_CACHE = None


def brands_observed(card_type, mid, oid=None):
  """Brands observed shipping under a card's MID (or, when oid is given and the table narrows it, its MID/OID).

  Returns a sorted list, empty when the pairing is unknown or thin - the caller then says nothing, so an unseen
  pairing reads neutral, never as a suspicion signal (ADR 0007 addendum). Cached: the model is derived once from
  the static table on first use.
  """
  global _BRAND_SETS_CACHE
  if _BRAND_SETS_CACHE is None:
    _BRAND_SETS_CACHE = brand_sets()
  entry = _BRAND_SETS_CACHE.get(card_type, {}).get(mid)
  if not entry:
    return []
  if oid is not None and oid in entry['by_oid']:
    return list(entry['by_oid'][oid])
  return list(entry['brands'])


def _check_brand_token(problems, where, brand):
  """Flag one brand token that a clean parse should never emit (empty, a placeholder, or a parse leak)."""
  if not isinstance(brand, str) or not brand.strip():
    problems.append('%s: brand token %r is empty or not a string' % (where, brand))
    return
  if brand.strip().lower() in _NON_BRANDS:
    problems.append('%s: brand token %r is a placeholder, not a brand' % (where, brand))
  if _BRAND_LEAK_RE.search(brand) or '(' in brand or ')' in brand:
    problems.append('%s: brand token %r still contains a separator/bracket (parse leak)' % (where, brand))


def validate_brand_sets(model=None):
  """Structurally validate the brand-set model (empty list == clean), the analogue of validate_cid_db.

  Because the model is *derived*, this guards the derivation itself: a regression that let a separator, bracket,
  placeholder or empty string leak into a brand set would quietly corrupt the signal, so CI checks the shipped
  model stays clean on every change. Accepts a model dict so the rejection classes can be tested directly.
  """
  if model is None:
    model = brand_sets()
  problems = []
  for card_type, mids in (model or {}).items():
    if card_type not in ('SD', 'MMC'):
      problems.append('top-level key %r is not SD or MMC' % card_type)
    if not isinstance(mids, dict):
      problems.append('%s: expected a dict of MID -> entry' % card_type)
      continue
    for mid, entry in mids.items():
      at = '%s/%s' % (card_type, mid)
      if not _MID_RE.match(str(mid)):
        problems.append('%s: MID key is not zero-padded lowercase hex like 0x000003' % at)
      if not isinstance(entry, dict) or 'brands' not in entry:
        problems.append('%s: entry has no brands set' % at)
        continue
      brands = entry.get('brands')
      if not isinstance(brands, (list, tuple)) or not brands:
        problems.append('%s: brands must be a non-empty list' % at)
      else:
        for brand in brands:
          _check_brand_token(problems, at, brand)
      by_oid = entry.get('by_oid', {})
      if not isinstance(by_oid, dict):
        problems.append('%s: by_oid must be a dict' % at)
        continue
      for oid, oid_brands in by_oid.items():
        oat = '%s/%s' % (at, oid)
        if not _OID_RE.match(str(oid)):
          problems.append('%s: OID key is not hex like 0x5344' % oat)
        if not isinstance(oid_brands, (list, tuple)) or not oid_brands:
          problems.append('%s: by_oid brands must be a non-empty list' % oat)
        else:
          for brand in oid_brands:
            _check_brand_token(problems, oat, brand)

  return problems
