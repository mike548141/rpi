"""rpi-sdinfo: native, dependency-free SD/MMC card identity, benchmark and counterfeit detection.

Runs on Raspberry Pi Linux, macOS and Windows using nothing but the Python standard library.
Public entry points:

* ``rpi_sdinfo.cli:main``    - the full identity + benchmark + fraud-check tool
* ``rpi_sdinfo.bench:main``  - the standalone native benchmark
* ``rpi_sdinfo.verify:main`` - the standalone capacity-fraud sweep

The single source of truth for the version is ``__version__`` below; ``pyproject.toml`` reads it
dynamically and ``cli`` imports it for ``--version`` and the JSON ``tool_version`` field.
"""

__version__ = "0.9.1"
