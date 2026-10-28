# Foundation validation

Use the pinned Rust 1.99.1 toolchain and the README commands for formatting, Clippy,
locked build, tests and a JSON report smoke test. These are read-only application tests;
the explicit v0.2 installer has separate tests below; no compositor or session activation exists.

## Linux and supported distribution

CI builds on Ubuntu and runs the resulting executable as UID 65534 in a disposable
Debian 13 container with networking disabled. Assertions verify Linux/Debian/release,
APT detection, a real local-cache query and a non-live-switch-capable KDE catalog.
The container may lack package indexes: unknown/unavailable are truthful results, not
installation failures. This tests local query execution, not current remote availability,
a resolved package transaction, full Wayland dependencies or graphics readiness.

CI publishes a seven-day `udm-linux-x86_64-test` artifact containing the executable
archive and Debian JSON report. This is a test artifact, not an end-user release.
Build and distribution licensing remain separate from this validation workflow.

## Offline LAN hardware smoke test

`miix320` is LAN-only and has no internet access. Use its existing SSH alias; do not
substitute a public endpoint or enable internet access. Its installed OS is CachyOS,
so the Debian package adapter must report unsupported there. No Rust toolchain is
required on the device: obtain the trusted build from the matching CI commit on the
Mac and transfer the executable over the LAN. Verify archive hashes before execution.
Run as the regular user from a uniquely named temporary directory, then remove only
those test files. Never use sudo, install packages or manipulate graphical sessions.

Check the JSON against /etc/os-release, uname and standard session definitions.
For the current host, expect two Hyprland Wayland entries, pacman detection, no KDE
Wayland entry, unsupported package querying and live_switch_capable=false. Compare a
hash of `pacman -Q` before/after to detect package inventory changes. This check does
not establish arbitrary window preservation or the absence of every possible side effect.

For Debian desktop compatibility, use a separate disposable Debian 13 test system;
CachyOS hardware cannot validate the release-specific APT adapter. Keep recorded results
in PROJECT_STATE.md and the relevant issue/PR, distinguishing observed from planned.

## v0.2 package workflow

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/packages -v`
for safety, journal and injected-failure tests without root or APT. The separate
Debian CI job provisions python3-apt in a disposable container and runs
`tests/packages/debian-simulation.sh` as nobody. It checks repeated native resolution,
no removal/upgrade/display-manager additions, honest pre-install verification and
identical before/after package inventory. It never installs KDE.

[Evidence and snapshot-VM acceptance blocker](validation/v0.2/README.md). Real
installation requires a newly reviewed VM-specific plan and explicit approval.
