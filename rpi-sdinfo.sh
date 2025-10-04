#!/bin/bash
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.1-20231017
# License:      GNU GPL v2
#

# Lookup table to find the silicon maker of the controller within the MMC/SD card, and the brand (make & model) of the MMC/SD card that the end user would recognise
# The MID and OID are defined, controlled and assigned by the SD-3C, LLC. They do not publish the list as they consider it to be confidential information, so this is all crowd sourced and really needs better data
# The array keys are as reported by the Linux kernel, within SD-3C CID they are referred to as Type, MID, OID, PNM, PRV (hardware).
# Key: type and manfid = The silicon maker of the storage controller
# Key: type, manfid, and oemid = Brand(s) of the MMC/SD card
# Key: type, manfid, oemid, name, and hwrev = A complete hardware match to the MMC/SD storage, as the firmware is sometimes upgradeable on MMC/SD cards I'm assuming that won't differentiate the product as the end user would recognise it
declare -A manufacturer_db=( \
  ['MMC','0x000000']='SanDisk' \
  ['MMC','0x000002']='Kingston, or SanDisk' \
  ['MMC','0x000003']='Toshiba' \
  ['MMC','0x000005']='Unknown' \
  ['MMC','0x000006']='Unknown' \
  ['MMC','0x000011']='Toshiba' \
  ['MMC','0x000013']='Micron' \
  ['MMC','0x000015']='Samsung, SanDisk, or LG' \
  ['MMC','0x000037']='KingMax' \
  ['MMC','0x000044']='ATP' \
  ['MMC','0x000045']='SanDisk Corporation' \
  ['MMC','0x000045','0x0100','SEM16','0x4']='ChromeBook Internal eMMC'          # CID:45010053454d31364790e03506aebf4d \\
  ['MMC','0x000070']='Kingston' \
  ['MMC','0x00002c']='Kingston' \
  ['MMC','0x0000fe']='Micron' \
  ['SD','0x000001']='Panasonic' \
  ['SD','0x000001','0x5041']='Panasonic' \
  ['SD','0x000002']='Kingston, Toshiba, or Viking' \
  ['SD','0x000002','0x544d']='Kingston, Toshiba, or Viking' \
  ['SD','0x000002','0x544d','SA64G','0x5']='Kingston 64 GB microSDXC U1 C10'    # CID:02544d534136344753292e67a2013343 \\
  ['SD','0x000002','0x544d','SD02G','0x2']='Kingston 2 GB SDSC'                 # CID:02544d534430324728ad78243300793d \\
  ['SD','0x000003']='SanDisk' \
  ['SD','0x000003','0x5054']='SanDisk' \
  ['SD','0x000003','0x5344']='SanDisk' \
  ['SD','0x000003','0x5344','SD02G','0x8']='SanDisk Blue 2 GB SDSC'             # CID:035344534430324780019acc7600844b \\
  ['SD','0x000003','0x5344','SU01G','0x8']='SanDisk Ultra II 1 GB microSDSC'    # CID:035344535530314780401c751300637d \\
  ['SD','0x000003','0x5344','SU32G','0x8']='SanDisk 32 GB microSDHC C4'         # CID:035344535533324780718848c800b7fb \\
  ['SD','0x000003','0x5344','SU64G','0x8']='SanDisk Ultra 64 GB microSDXC U1'   # CID:0353445355363447801013d98600d6d3 \\
  ['SD','0x000008']='Silicon Power' \
  ['SD','0x000012','0x3456','MS','0x1']='Unbranded 2 GB microSDSC'              # CID:1234564d532020201000004c6300c853 \\
  ['SD','0x000012','0x5678','ASTC','0x3']='Strontium 16 GB microSDHC C10'       # CID:1256784153544300340000059b01032f \\
  ['SD','0x000018']='Infineon' \
  ['SD','0x000027']='Phison Electronics Corporation' \
  ['SD','0x000027','0x5048']='AgfaPhoto, Delkin, Integral, Lexar, Patriot, PNY, Polaroid, Sony, or Verbatim' \
  ['SD','0x000027','0x5048','SD32G','0x3']='Patriot 32 GB SDHC C10'             # CID:275048534433324730b018bd6700abe5 \\
  ['SD','0x000028']='Lexar' \
  ['SD','0x000028','0x4245']='Lexar, PNY, or ProGrade' \
  ['SD','0x000030']='SanDisk' \
  ['SD','0x000031']='Silicon Power' \
  ['SD','0x000031','0x5350']='Silicon Power' \
  ['SD','0x000033']='STMicroelectronics' \
  ['SD','0x000041']='Kingston' \
  ['SD','0x000041','0x3432']='Kingston' \
  ['SD','0x000041','0x3432','SD128','0x3']='Kingston 128 GB SDXC C10'           # CID:41343253443132383002b800b600da6f \\
  ['SD','0x00006f']='STMicroelectronics' \
  ['SD','0x000074']='Transcend' \
  ['SD','0x000074','0x4a45']='Transcend' \
  ['SD','0x000074','0x4a60']='Transcend' \
  ['SD','0x000076']='Patriot' \
  ['SD','0x000082']='Gobe, or Sony' \
  ['SD','0x000082','0x4a54']='Gobe, or Sony' \
  ['SD','0x000088','0x0302','1232','0x1']='Pretec 2 GB microSDSC'               # CID:8803023132333220100000cea40071b9  \\
  ['SD','0x000089']='Unknown' \
  ['SD','0x000089','0x0303','NCard','0x0']='Team 32 GB C10'                     # CID:8903034e43617264000000667000b285 \\
  ['SD','0x00001b']='Samsung, or Transcend' \
  ['SD','0x00001b','0x534d']='Samsung, or ProGrade' \
  ['SD','0x00001b','0x534d','00000','0x1']='Raspberry Pi BMC SDHC'              # CID:1b534d3030303030100337410200d13b \\
  ['SD','0x00001b','0x534d','00000','0x1']='Samsung 32 GB SDHC C10'             # CID:1b534d3030303030107d11463800c199 \\
  ['SD','0x00001c']='Transcend' \
  ['SD','0x00001d']='AData, or Corsair' \
  ['SD','0x00001d','0x4144']='AData' \
  ['SD','0x00001e']='Transcend' \
  ['SD','0x00001f']='Kingston' \
  ['SD','0x00009c','0x534f']='Angelbird (V60), or Hoodman' \
  ['SD','0x00009c','0x4245']='Angelbird (V90)' \
)

declare -A RPi=( \
  ['model']=$(tr -d '\0' </sys/firmware/devicetree/base/model) \
  ['serial']=$(tr -d '\0' </sys/firmware/devicetree/base/serial-number) \
  ['mac_eth0']=$(</sys/class/net/eth0/address) \
  ['mac_wlan0']=$(</sys/class/net/wlan0/address) \
  ['mac_bt0']=$(sudo cat /sys/kernel/debug/bluetooth/hci0/identity | cut -d' ' -f1) \
  ['os']=$(grep 'PRETTY_NAME' /etc/os-release | sed 's/PRETTY_NAME="\(.*\)"/\1/g') \
  ['kernel']=$(uname -r) \
)

declare -A card=( \
  ['type']=$(</sys/block/mmcblk0/device/type) \
  ['read_only']=$(</sys/block/mmcblk0/ro)                   # Hardware boolean to force read only, on SD cards thats controlled by a switch on its side \\
  ['force_read_only']=$(</sys/block/mmcblk0/force_ro)       # Software boolean to force read only \\
  ['removable']=$(</sys/block/mmcblk0/removable) \
  ['blocks']=$(</sys/block/mmcblk0/size) \
  ['block_size']=$(</sys/block/mmcblk0/device/erase_size) \
  ['ocr']=$(</sys/block/mmcblk0/device/ocr)                 # Operation Conditions Register \\
  ['cid']=$(</sys/block/mmcblk0/device/cid)                 # Card Identification register is 16 bytes (128 bits) code that contains information that uniquely identifies the MMC/SD card \\
  ['cid_mid']=$(</sys/block/mmcblk0/device/manfid)          # Manufacturer ID (from CID Register). 8-bit number that identifies the manufacturer, assigned by SD-3C \\
  ['cid_oid']=$(</sys/block/mmcblk0/device/oemid)           # OEM/Application ID (from CID Register). 2-character ASCII string that identifies the card OEM and/or the card contents, assigned by SD-3C \\
  ['cid_pnm']=$(</sys/block/mmcblk0/device/name)            # Product Name (from CID Register). 5-character ASCII string \\
  ['cid_prv_hw']=$(</sys/block/mmcblk0/device/hwrev)        # Hardware/Product Revision (from CID Register) (SD and MMCv1 only). PRV is composed of two Binary Coded Decimal (BCD) digits, four bits each, representing an “n.m” revision number \\
  ['cid_prv_fw']=$(</sys/block/mmcblk0/device/fwrev)        # Firmware/Product Revision (from CID Register) (SD and MMCv1 only). PRV is composed of two Binary Coded Decimal (BCD) digits, four bits each, representing an “n.m” revision number \\
  ['cid_psn']=$(</sys/block/mmcblk0/device/serial)          # Product serial number is 32 bits ordinary number \\
  ['cid_mdt']=$(</sys/block/mmcblk0/device/date)            # Manufacturing Date (from CID Register), composed of 12 bits in YYM format, (offset from 2000) \\
  ['csd']=$(</sys/block/mmcblk0/device/csd)                 # Card Specific Data register \\
  ['rca']=$(</sys/block/mmcblk0/device/rca)                 # Relative Card Address register \\
  ['dsr']=$(</sys/block/mmcblk0/device/dsr)                 # Driver Stage Register \\
  ['scr']=$(</sys/block/mmcblk0/device/scr)                 # SD Card Configuration Register (SD only) \\
  ['ssr']=$(</sys/block/mmcblk0/device/ssr)                 # SD Status Register \\
)

declare -A fs_info=( \
  ['state']=$(sudo dumpe2fs -h /dev/mmcblk0p2 2> /dev/null | grep 'Filesystem state: ' | sed 's/Filesystem state: *//g') \
  ['created']=$(sudo dumpe2fs -h /dev/mmcblk0p2 2> /dev/null | grep 'Filesystem created: ' | sed 's/Filesystem created: *//g') \
  ['last_checked']=$(sudo dumpe2fs -h /dev/mmcblk0p2 2> /dev/null | grep 'Last checked: ' | sed 's/Last checked: *//g') \
  ['mount_count']=$(sudo dumpe2fs -h /dev/mmcblk0p2 2> /dev/null | grep 'Mount count: ' | sed 's/Mount count: *//g') \
  ['last_mount']=$(sudo dumpe2fs -h /dev/mmcblk0p2 2> /dev/null | grep 'Last mount time: ' | sed 's/Last mount time: *//g') \
)

# Make and model
card['manufacurer']=${manufacturer_db[${card[type]},${card[cid_mid]}]}
if [ -z "${card['manufacurer']}" ]
then
  card['manufacurer']='unknown'
fi
card['brand']=${manufacturer_db[${card[type]},${card[cid_mid]},${card[cid_oid]}]}
if [ -z "${card['brand']}" ]
then
  card['brand']=${card['manufacurer']}
fi
card['label']=${manufacturer_db[${card[type]},${card[cid_mid]},${card[cid_oid]},${card[cid_pnm]},${card[cid_prv_hw]}]}
if [ -z "${card['label']}" ]
then
  card['label']=${card['brand']}
fi

# Linux kernel dictates that for SD, "erase_size" is 512 if the card is block-addressed, 0 otherwise. This does not handle a zero value
card['bytes']=$(( ${card[blocks]} * ${card[block_size]} ))
card['GB']=$(printf "%.2f" $((${card[bytes]} / 1000000000)))
card['GiB']=$(printf "%.2f" $((${card[bytes]} / 1024 / 1024 / 1024)))

# Card state
if [ ${card[read_only]} = 0 ] && [ ${card[force_read_only]} = 0 ]
then
  card['state']='read/write'
elif [ ${card[read_only]} = 1 ] && [ ${card[force_read_only]} = 1 ]
then
  card['state']='read only (hardware+software)'
elif [ ${card[read_only]} = 1 ]
then
  card['state']='read only (hardware)'
elif [ ${card[force_read_only]} = 1 ]
then
  card['state']='read only (software)'
fi
if [ ${card['removable']} = 0 ]
then
  card['removable_label']='not removable'
elif [ ${card['removable']} = 1 ]
then
  card['removable_label']='removable'
fi

# System info
echo -e "\n${RPi['model']} with serial: ${RPi['serial']}\n   Has been $(uptime --pretty) running ${RPi['os']}, kernel ${RPi['kernel']}"
echo -e "   Ethernet MAC:  ${RPi['mac_eth0']}\n   WiFi MAC:      ${RPi['mac_wlan0']}\n   Bluetooth MAC: ${RPi['mac_bt0']}"
# Storage info
echo -e "\nThe ${card[type]} storage is a ${card['label']}"
echo -e "   Capacity:                    ${card['GB']} GB (${card['GiB']} GiB, ${card[blocks]} blocks of ${card[block_size]} bytes)\n   Manufacturers serial number: ${card[cid_psn]}\n   Manufacture date (mm/yyyy):  ${card[cid_mdt]}"
echo -e "   The ${card['manufacurer']} storage controller is running firmware revision ${card[cid_prv_fw]}\n   The card is ${card['state']} and is ${card['removable_label']}"
echo -e "\nThe Filesystem of mmcblk0p2 is ${fs_info['state']}\n   Created:      ${fs_info['created']}\n   Last checked: ${fs_info['last_checked']}\n   Mounted:      ${fs_info['mount_count']} times\n   Last mounted: ${fs_info['last_mount']}"
echo -e "\n${card[type]} Registers:\n   OCR: ${card['ocr']}\n   CID: ${card['cid']}\n   CSD: ${card['csd']}\n   RCA: ${card['rca']}\n   DSR: ${card['dsr']}\n   SCR: ${card['scr']}\n   SSR: ${card['ssr']}"

# System load info
declare -a cpu_stats=( $(</proc/loadavg) )
if [[ "${cpu_stats[0]}" > "0.49" ]] && [[ "${cpu_stats[1]}" > "0.69" ]] && [[ "${cpu_stats[2]}" > "0.69" ]]
then
  cpu_stats+=('Warning high CPU load!!')
fi
declare -a mem_stats=( $(free --wide --mebi | grep '^Mem:') )
declare -a disk_stats=( $(grep ' mmcblk0 ' /proc/diskstats) )
echo -e "\n CPU load average (1m): ${cpu_stats[0]}    ${cpu_stats[5]}\n                  (5m): ${cpu_stats[1]}\n                 (15m): ${cpu_stats[2]}\nThreads (active/total): ${cpu_stats[3]}"
echo -e "                Memory: ${mem_stats[3]} MiB free of ${mem_stats[1]} MiB total"
echo -e " Storage ${disk_stats[2]} reads: ${disk_stats[3]} from ${disk_stats[5]} sectors in ${disk_stats[7]} ms\n                writes: ${disk_stats[7]} to ${disk_stats[9]} sectors in ${disk_stats[10]} ms\n              discards: ${disk_stats[14]} from ${disk_stats[16]} sectors in ${disk_stats[17]} ms\n               flushes: ${disk_stats[18]} in ${disk_stats[19]} ms\n            Active I/O: ${disk_stats[11]} in ${disk_stats[12]} ms (weighted ${disk_stats[13]} ms)\n"

# Ensure fio is installed for storage speed testing
if [ "$(dpkg-query --status fio | grep 'Status: ')" != "Status: install ok installed" ]
then
  echo -e '\n\nYou need to install fio to run a speed test\nsudo apt -y install fio\n\n'
fi

sudo mkdir --parents '/usr/share/fio'
echo -e '# Use FIO to emulate the Apps Class A1 performance test.\n# This is not an exact benchmark as the card is not in the state required by the\n# specification, but is good enough as a sniff test.\n#\n[global]\nioengine=libaio\niodepth=4\nsize=64m\ndirect=1\nend_fsync=1\ndirectory=/var/tmp\nfilename=sd.test.file\n\n[prepare-file]\nrw=write\nbs=512k\nstonewall\n\n[seq-write]\nrw=write\nbs=512k\nstonewall\n\n[rand-4k-write]\nrw=randwrite\nbs=4k\nruntime=10\nstonewall\n\n[rand-4k-read]\nrw=randread\nbs=4k\nruntime=10\nstonewall\n\n# execute with command $ fio --output-format=terse sd_bench.fio | cut -f 3,7,8,48,49 -d";" -\n# testname, read bandwidth, read iops, write bandwidth, write iops' | sudo tee /usr/share/fio/sd_bench.fio > /dev/null

for test_run in 1 2 3
do
  echo -n "Run ${test_run}"
  
  
  
  results=$(fio --output-format=terse --max-jobs=4 /usr/share/fio/sd_bench.fio | cut -f 3,7,8,48,49 -d";" -)
  results_seq_write=$(echo "${results}" | head -n 2 | tail -n 1 | cut -d ";" -f 4)
  results_rand_write=$(echo "${results}" | head -n 3 | tail -n 1 | cut -d ";" -f 5)
  results_rand_read=$(echo "${results}" | head -n 4 | tail -n 1 | cut -d ";" -f 3)
  
  
  
  echo -e ": Sequential Writes: ${results_seq_write} KBps ${} IOPS   Random 4 KiB writes: ${} MBps ${results_rand_write} IOPS   Random 4 KiB reads: ${} MBps ${results_rand_read} IOPS"
  
  
  
  
  echo "${RES}"
  swri=$(echo "${RES}" | head -n 2 | tail -n 1 | cut -d ";" -f 4)
  rwri=$(echo "${RES}" | head -n 3 | tail -n 1 | cut -d ";" -f 5)
  rrea=$(echo "${RES}" | head -n 4 | tail -n 1 | cut -d ";" -f 3)
  pass=0
  if [ "${swri}" -lt 10000 ] ; then
    echo "Sequential write speed ${swri} KB/sec (target 10000) - FAIL"
    echo "Note that sequential write speed declines over time as a card is used - your card may require reformatting"
    pass=1
  else
    echo "Sequential write speed ${swri} KB/sec (target 10000) - PASS"
  fi
  if [ "$rwri" -lt 500 ] ; then
    echo "Random write speed ${rwri} IOPS (target 500) - FAIL"
    pass=1
  else
    echo "Random write speed ${rwri} IOPS (target 500) - PASS"
  fi
  if [ "$rrea" -lt 1500 ] ; then
    echo "Random read speed ${rrea} IOPS (target 1500) - FAIL"
    pass=1
  else
    echo "Random read speed ${rrea} IOPS (target 1500) - PASS"
  fi
  rm -f /var/tmp/sd.test.file
  if [ "${pass}" -eq 0 ] ; then
    return ${pass}
  fi
done
#return $pass


#CSD:
#2.5 x 10Mbit/s
#Class 0: Yes. Class 1: No. Class 2: Yes. Class 3: No. Class 4: Yes. Class 5: Yes. Class 6: No. Class 7: Yes. Class 8: Yes. Class 9: No. Class 10: Yes. Class 11: No
#Write Speed Factor

#Bus: UHS-I, UHS-II, UHS-III
#C2 2 MBps, C4 4 MBps, C6 6 MBps, C10 10 MBps
#U1 10 MBps, U3 30 MBps
#V6, V10, V30, V60, V90 MBps
#Application Performance Class 1 (A1), Min Rand Read: 1500 IOPS, Min Rand Write: 500 IOPS, Min sustained seq write: 10 MBps
#Application Performance Class 2 (A2), Min Rand Read: 4000 IOPS, Min Rand Write: 2000 IOPS, Min sustained seq write: 10 MBps

#mmc csd read /sys/block/mmcblk0/device
#mmc scr read /sys/block/mmcblk0/device

## A way to true test the size for fake cards
## Convert SD association codes to names https://github.com/mhei/mmc-utils/blob/613495ecaca97a19fa7f8f3ea23306472b36453c/lsmmc.c
## Search logs for error messages relative to MMC

# Decode CSD
#if [ ${card[csd]:1:1} = '0' ]
#then
#  card['csd_structure']='Version 1.0 standard capacity (SDSC)'
#elif [ ${card[csd]:1:1} = '1' ]
#then
#  card['csd_structure']='Version 2.0 high capacity (SDHC) and extended capacity (SDXC)'
#fi
#echo "${card['csd_structure']}"
