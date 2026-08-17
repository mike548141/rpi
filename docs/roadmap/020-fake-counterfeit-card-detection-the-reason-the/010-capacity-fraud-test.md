- [ ] **Capacity fraud test.** ✅ Shipped in 0.6 (`sdverify.py`, `--capacity-check`) and since extended with a
      raw-device **corners sweep** (`sdverify.py --device`): probes block 0, every power-of-two offset, and the last
      block of the reported capacity. Because a fake truncates the block address at a power-of-two boundary R, block
      0 and block R alias onto one physical cell, so the (0, R) pair is always probed — a guaranteed catch for any
      power-of-two address-truncation fake (the standard kind) in ~log₂(N) probes rather than a full-card write.
      Destructive, so gated behind `--yes` and a mounted-device refusal. Still to refine:
      - **Non-power-of-two wraps.** ✅ The corners sweep now also probes each common decimal capacity boundary below
        the reported size (`COMMON_FAKE_CAPACITIES_BYTES`), so a fake that wraps at a round decimal size (e.g. a real
        8 GB chip reporting 512 GB) aliases that boundary onto block 0 and is caught. A *truly arbitrary* wrap (no
        round boundary) can still slip past both the power-of-two and decimal probes; the thorough free-space sweep
        remains the exhaustive backstop, so corners stays a fast first-pass, not a replacement.
      - **Wire the corners sweep into `rpi-sdinfo`** (e.g. `--capacity-check --raw --device …`) once it can be tested
        on a real removable card - deliberately not auto-wired yet, since a destructive raw write to the wrong
        device must not ship untested on hardware.
      - Raw-device *full* sweep (not just corners) where we have the device and privileges, so a nearly-full card
        can still be exhaustively tested without needing free space. ✅ Shipped **file-tested** as
        `rpi-sdverify --device … --full`: writes then verifies *every* block of the reported capacity
        (write-all-then-verify-all, streamed block-by-block, no device data held in RAM), so a nearly-full card is
        tested by overwriting it and an *arbitrary* wrap the corners/decimal probes miss is caught. Same gates as
        corners (`--yes`, mounted-device refusal). **Hardware validation still owed** — like the corners raw-write
        path, it has not been run against a real removable card; that joins the Pi-hardware blocker watch above
        before it can be trusted end-to-end or auto-wired into `rpi-sdinfo`.
