- [ ] 🛑 **Not yet hardware-tested on a Pi.** The macOS path is exercised end-to-end (and now unit-tested); the Linux
      `gather_linux()` path is preserved from the working 0.3 logic and compiles, but the sysfs-dependent parts still
      need a run on a real Pi 3B and Pi Zero W. Watch:
      - `sdbench` write/read units and whether the F_NOCACHE/O_DSYNC path reports realistic SD numbers on a Pi
        (validate against the old fio results and a known card).
      - `dumpe2fs` / `meminfo` label spellings across Raspberry Pi OS versions.
      - `/proc/diskstats` column count/order for the read/write counters.
      - The new `erase_size == 0` branch: confirm a real not-block-addressed card actually reports 0 and that the
        assumed-512 capacity + `info` flag read sensibly (only the pure logic is unit-tested; the sysfs read is not).
