# macOS identity helpers: the built-in-reader product resolver and the mount-point picker used by removable-card
# auto-detection. Pure logic (subprocess-free), so it runs on any platform in CI - the diskutil/system_profiler
# shell-outs that feed them are the untestable-without-hardware part and are kept thin on purpose.
import unittest

from _loader import load_sdinfo

sdinfo = load_sdinfo()

# A plausible `system_profiler -json SPCardReaderDataType` shape: the reader node carries the inserted card under
# '_items', and the card node exposes its own product (_name), make and serial keyed by BSD device name.
CARD_READER_TREE = [
  {
    '_name': 'spcardreader',
    'spcardreader_vendor-id': '0x05ac',
    '_items': [
      {
        '_name': 'SDXC Card',
        'bsd_name': 'disk4',
        'spmemorycard_manufacturer': 'SanDisk',
        'spmemorycard_serial_number': '0xA1B2C3D4',
        'size': '63.9 GB',
      }
    ],
  }
]


class MacosCardIdentity(unittest.TestCase):
  def test_matches_nested_card_by_bsd_name(self):
    ident = sdinfo.macos_card_identity('disk4', tree=CARD_READER_TREE)
    self.assertEqual(ident['product'], 'SDXC Card')
    self.assertEqual(ident['manufacturer'], 'SanDisk')
    self.assertEqual(ident['serial'], '0xA1B2C3D4')

  def test_absent_device_returns_empty(self):
    self.assertEqual(sdinfo.macos_card_identity('disk9', tree=CARD_READER_TREE), {})

  def test_empty_tree_returns_empty(self):
    self.assertEqual(sdinfo.macos_card_identity('disk4', tree=[]), {})

  def test_partial_node_only_returns_present_fields(self):
    tree = [{'_items': [{'bsd_name': 'disk4', '_name': 'SD Card'}]}]
    self.assertEqual(sdinfo.macos_card_identity('disk4', tree=tree), {'product': 'SD Card'})

  def test_blank_values_are_ignored(self):
    tree = [{'_items': [{'bsd_name': 'disk4', '_name': '  ', 'spmemorycard_manufacturer': ''}]}]
    self.assertEqual(sdinfo.macos_card_identity('disk4', tree=tree), {})


class FindCardNode(unittest.TestCase):
  def test_depth_first_through_items(self):
    node = sdinfo._find_card_node(CARD_READER_TREE, 'disk4')
    self.assertEqual(node.get('_name'), 'SDXC Card')

  def test_tolerates_non_dict_nodes(self):
    tree = ['noise', 42, {'_items': ['x', {'bsd_name': 'disk4', '_name': 'ok'}]}]
    self.assertEqual(sdinfo._find_card_node(tree, 'disk4').get('_name'), 'ok')


class EntryMountpoint(unittest.TestCase):
  def test_first_plain_partition_mount_wins(self):
    entry = {'Partitions': [{'DeviceIdentifier': 'disk4s1'},
                            {'DeviceIdentifier': 'disk4s2', 'MountPoint': '/Volumes/CARD'}]}
    self.assertEqual(sdinfo._entry_mountpoint(entry), '/Volumes/CARD')

  def test_falls_through_to_apfs_volume(self):
    entry = {'Partitions': [{'DeviceIdentifier': 'disk4s1'}],
             'APFSVolumes': [{'MountPoint': '/Volumes/APFSCARD'}]}
    self.assertEqual(sdinfo._entry_mountpoint(entry), '/Volumes/APFSCARD')

  def test_nothing_mounted_returns_empty(self):
    self.assertEqual(sdinfo._entry_mountpoint({'Partitions': [{'DeviceIdentifier': 'disk4s1'}]}), '')

  def test_missing_keys_return_empty(self):
    self.assertEqual(sdinfo._entry_mountpoint({}), '')


if __name__ == '__main__':
  unittest.main()
