- [x] **macOS: removable-card auto-detect and real card identity.**
      ✅ Auto-detect a removable card when `--device`/`--dir` is omitted (scans for a removable/external whole
      disk, prefers an SD-bus reader, and points the benchmark at its mount point), and ✅ resolve the card's real
      product/make/serial from a **built-in SD slot** via `system_profiler SPCardReaderDataType`. USB card readers
      still present as generic mass storage, so their card product name remains reader-dependent — no macOS API
      exposes an SD card's CID through a generic USB reader.
