"""Allow ``python -m rpi_sdinfo`` to run the full tool (equivalent to the ``rpi-sdinfo`` script)."""

import sys

from .cli import main

if __name__ == "__main__":
  sys.exit(main())
