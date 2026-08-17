- [ ] **`sdbench`: a true O_DIRECT path on Linux.**
      Optional, with aligned buffers, for the most accurate device-level numbers.
      ✅ Latency percentiles (not just the mean) shipped in 0.8. ✅ **Progressively-larger block sizes** shipped as
      `rpi-sdbench --block-sweep` (post-0.9.1): an opt-in sequential-write throughput-vs-block-size curve (4 KiB →
      1 MiB), diagnostic of a controller whose small-block writes collapse or never scale. The O_DIRECT path still
      needs a real Pi to validate.
