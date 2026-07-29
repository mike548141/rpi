# Security policy

`rpi-sdverify --device` deliberately writes to raw block devices and is typically run
with elevated privileges. A bug in that path can destroy data on the wrong disk, so
reports about unsafe device handling, privilege handling or data-destruction paths are
especially welcome — alongside anything else you'd call a vulnerability.

## Reporting a vulnerability

Please report suspected vulnerabilities **privately** through GitHub:

- [Report a vulnerability](https://github.com/mike548141/rpi/security/advisories/new)
  (the repo's **Security** tab → *Report a vulnerability*).

Please do **not** open a public issue for a suspected vulnerability. You can expect an
acknowledgement within a week; disclosure is coordinated — the advisory is published
once a fixed release is available.

## Supported versions

Pre-1.0, only the latest release and `main` receive fixes.
