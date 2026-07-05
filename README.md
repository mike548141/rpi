# rpi
Raspberry Pi tools

If I make more tools then I will add them here, but currently this is just one tool called rpi-sdinfo.

## rpi-sdinfo
A script to (a) test the performance and integrity of SD cards, (b) try and spot genuine/fake SD cards. I wrote the original in bash but then I started to re-write it in python. Neither are completely finished for a v1.0 but its a solid start.
If it was useful then I would probably build a public web service where everyone could share their results to build up a database of SD card identifiers, performance, and failure rates.

`rpi-sdinfo.py` is the version being developed; `rpi-sdinfo.sh` is kept for reference only. The Python version now
reports the Pi and card details, benchmarks the card with fio, and grades the measured performance against the
card's rated speed class (PASS/FAIL, falling back to A1). It requires a Raspberry Pi running Raspberry Pi OS with
the `fio` package installed (`sudo apt -y install fio`); run it with `sudo` so it can read every register.

See [ROADMAP.md](ROADMAP.md) for what's done and what's still planned before v1.0 — including hardware testing,
counterfeit-capacity detection, and the shared results database.
