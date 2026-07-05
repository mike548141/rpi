# SD / MMC cards: identifying them and knowing what to expect

Background reference for `rpi-sdinfo`. It covers how a card identifies itself, how to read the branding
symbols on the label, what performance each class promises, and how to smell a fake. Sources are the SD
Association's public specifications and the crowd-sourced CID data this tool ships with — the manufacturer/OEM
ID list is *not* published by SD-3C, so it is assembled from real cards and is necessarily incomplete.

## 1. How a card identifies itself — the CID register

Every SD/MMC card carries a 16-byte **CID** (Card IDentification) register, burned in at manufacture. Linux
exposes its fields under `/sys/block/mmcblk0/device/`; macOS does **not** expose them at all (this is why
`rpi-sdinfo` gives full identity only on a Raspberry Pi). The fields:

| Field | sysfs file | Meaning |
|-------|-----------|---------|
| MID (Manufacturer ID) | `manfid` | 8-bit maker of the **controller silicon**, assigned by SD-3C. e.g. `0x03` = SanDisk, `0x1b` = Samsung, `0x74` = Transcend |
| OID (OEM/Application ID) | `oemid` | 2-char ASCII identifying the **card brand/OEM**. Often shared by several resellers |
| PNM (Product Name) | `name` | 5-char ASCII product code, e.g. `SU64G`, `SD128` |
| PRV (Product Revision) | `hwrev` / `fwrev` | Hardware and firmware revision, two BCD digits ("n.m") |
| PSN (Serial Number) | `serial` | 32-bit unit serial |
| MDT (Manufacturing Date) | `date` | Month/year, encoded YYM as an offset from 2000 |

**Key insight for spotting fakes:** the MID identifies who made the *controller*, not necessarily the brand on
the label. A card sold as "SanDisk" whose MID belongs to a different silicon vendor is not automatically fake
(some brands second-source controllers), but a MID that has *never* been associated with the brand on the label
is a strong red flag. `rpi-sdinfo` resolves MID → controller maker, MID+OID → brand(s), and the full
MID+OID+PNM+PRV → a specific known product where the crowd-sourced data has a match.

The MID/OID assignments are confidential (SD-3C does not publish them), so the lookup table in `rpi-sdinfo.py`
is community-sourced. Contributions of new `CID → product` mappings are the single most valuable thing to add.

## 2. Reading the label — the branding symbols

SD card labels are a dense stack of logos. Each symbol is a *promise* about a minimum performance, defined by
the SD Association. From left to right you typically see:

### Capacity family (the SD tier)
| Symbol | Family | Capacity range | Filesystem (as shipped) |
|--------|--------|----------------|-------------------------|
| **SD** | Standard Capacity (SDSC) | up to 2 GB | FAT16 |
| **SDHC** | High Capacity | 2 GB – 32 GB | FAT32 |
| **SDXC** | eXtended Capacity | 32 GB – 2 TB | exFAT |
| **SDUC** | Ultra Capacity | 2 TB – 128 TB | exFAT |

### Speed Class (sustained sequential write floor)
Three overlapping systems exist; a card may show several. All numbers are the **minimum sustained sequential
write** in MB/s (base-10):

| Symbol | Name | Min sequential write |
|--------|------|----------------------|
| C2 / C4 / C6 | Speed Class (the number in a **C**) | 2 / 4 / 6 MB/s |
| **C10** | Speed Class 10 | 10 MB/s |
| **U1** | UHS Speed Class 1 (number in a **U**) | 10 MB/s |
| **U3** | UHS Speed Class 3 | 30 MB/s |
| **V6 / V10 / V30 / V60 / V90** | Video Speed Class (**V**n) | 6 / 10 / 30 / 60 / 90 MB/s |

### Application Performance Class (random IOPS — the one that matters for a Raspberry Pi OS drive)
This is what makes a card feel fast or slow as a *computer's* drive, because an OS does lots of small random IO:

| Symbol | Min random read | Min random write | Min sustained sequential write |
|--------|-----------------|------------------|-------------------------------|
| **A1** | 1500 IOPS | 500 IOPS | 10 MB/s |
| **A2** | 4000 IOPS | 2000 IOPS | 10 MB/s |

> For a Raspberry Pi, **A1/A2 random IOPS matter far more than the headline sequential MB/s**. A "95 MB/s"
> card with no A-rating can feel slower running an OS than a modest A1 card. This is exactly why `rpi-sdinfo`
> grades random read/write IOPS, and falls back to the A1 targets when a card declares no application class.

### Bus interface (the theoretical ceiling)
| Symbol | Bus | Theoretical max |
|--------|-----|-----------------|
| (none) / **I** | Default / High Speed | 12.5 / 25 MB/s |
| **UHS-I** (I) | Ultra High Speed I | 50 (SDR50) – 104 (SDR104) MB/s |
| **UHS-II** (II) | second row of pins | ~156–312 MB/s |
| **UHS-III** (III) | | ~312–624 MB/s |
| **SD Express** (with PCIe/NVMe logo) | PCIe/NVMe | 985 – ~3940 MB/s |

The bus is a *ceiling*, not a floor — and the host matters. **A Raspberry Pi 3/4/Zero's SD interface tops out
around DDR50 (~50 MB/s in ideal conditions, often ~20–45 MB/s real).** A UHS-II or SD Express card will not go
faster than the Pi's single-row SDR bus; you are paying for headroom the Pi can't use. So a Pi benchmark
showing ~45 MB/s sequential on a V90 card is the *Pi's* limit, not a bad card.

## 3. What to realistically expect on a Raspberry Pi

- **Sequential write:** ~20–45 MB/s is normal on a Pi 3/Zero regardless of the card's rating, because the host
  bus is the bottleneck. A card that manages <10 MB/s is failing even the humble C10/A1 floor.
- **Random 4K read:** a decent A1 card should clear ~1500 IOPS; A2 cards ~4000+. Cheap no-name cards often
  deliver a few hundred — miserable as an OS drive.
- **Random 4K write:** the hardest test. A1 = 500 IOPS, A2 = 2000. This is where worn or fake cards collapse.
- **Degradation over time:** sequential write speed **declines as a card fills and wears** (flash needs
  erase-before-write, and the FTL runs out of pre-erased blocks). A card that fails sequential write may just
  need reformatting (a full/secure erase, not a quick format) to restore pre-erased blocks. `rpi-sdinfo` prints
  this hint on a sequential-write failure.

## 4. Spotting fake / counterfeit cards

Counterfeits are common, especially high-capacity "bargains". Tell-tales, in rough order of reliability:

1. **Capacity fraud (the big one).** The card reports (say) 512 GB but physically holds far less; writes past
   the real capacity silently wrap or vanish, corrupting data. The *only* sure test is to **write data across
   the full claimed capacity and read it back** (tools like `f3`/`h2testw` do this; a native version is on the
   `rpi-sdinfo` roadmap). Reported capacity alone proves nothing.
2. **Performance far below the label.** A card branded U3/A2 that can't beat the C10/A1 floor is either fake,
   worn out, or grey-market rebadged. This is what `rpi-sdinfo`'s grading catches.
3. **CID inconsistency.** MID/OID that don't match the branded maker, a manufacture date in the future, an
   implausible serial, or a product name that doesn't exist in that maker's line-up.
4. **Physical tells.** Sloppy printing, mismatched fonts, a missing or wrong hologram, weight/flex differences,
   an unbranded generic controller behind a premium label.
5. **Too cheap.** A 1 TB A2 V30 card for a few dollars is not a deal, it is a re-programmed 32 GB card.

If in doubt: run a full-capacity write/verify, and compare measured performance and CID against the branding.
Sharing verified `CID → real product + measured performance` results is what would let a community database
flag fakes reliably — the long-term goal behind this tool.

## 5. Glossary

- **MMC / eMMC** — MultiMediaCard; eMMC is the soldered-down variant inside phones, ChromeBooks, some SBCs.
- **FTL** — Flash Translation Layer, the controller firmware that maps logical blocks to physical flash and
  does wear levelling; its state is why performance varies run to run and declines with wear.
- **IOPS** — IO Operations Per Second; the random small-block metric that dominates OS responsiveness.
- **SD-3C, LLC** — the entity that licenses SD tech and assigns MID/OID values (kept confidential).
- **Base-10 vs base-2** — storage is marketed in base-10 (1 GB = 1,000,000,000 bytes); RAM and "GiB" are
  base-2 (1 GiB = 1,073,741,824 bytes). `rpi-sdinfo` reports GB for the card and MiB for memory to match how
  each is conventionally branded.
