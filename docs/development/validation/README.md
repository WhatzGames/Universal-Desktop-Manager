# Validation evidence — 2026-10-28

Source commit: `1e967726ee962b7d718a2c1fa25192b6cea4fde7` (application code unchanged
from the original foundation; CI adds supported-distro and offline-artifact checks).
Rust: 1.99.1. CI: https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40773101833
PR checks: https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40773110954
Both runs passed formatting, Clippy, build, six tests, Ubuntu report, Debian report
assertions and test-artifact packaging. Raw sanitized reports are stored beside this file.

## Debian 13 container

The Linux executable ran as UID 65534 with container networking disabled. It detected
Debian 13 and apt-cache, then successfully ran local package policy. Availability is
unknown because the disposable base image has no usable KDE candidate metadata. This
is evidence that the real query path executes, not proof that KDE can be installed.
Unit tests separately cover candidate, no-candidate and failed/ambiguous output parsing.

## miix320 offline LAN test

Observed OS: CachyOS rolling, x86_64, Linux 7.2.7-1-cachyos, glibc 2.44. SSH connection
and application execution succeeded as UID 1000. No Rust toolchain was installed there.
The CI archive was transferred only over the LAN; its SHA-256 matched on both machines:
`dec9628a33cafe52e3726d85298bd02f96b8b03be4157c0217e87e71d531635b`.

The report matched /etc/os-release and the two inspected Wayland definitions:
hyprland.desktop and hyprland-uwsm.desktop. It detected pacman, no KDE Wayland entry,
unsupported CachyOS package querying and live_switch_capable=false. Version is unknown
because this rolling release provides BUILD_ID but no VERSION_ID.

SHA-256 of `pacman -Q` was identical before/after:
`3d9c96ffe4d628281ee9c45ff4cb80adaedb10491280b631a9df7c176406169b`.
No packages, system configuration or sessions were changed by the test. Only a unique
/tmp test directory and its archive/executable were created; both files and the directory
were removed afterward. The disconnected device clock lagged CI timestamps, producing a
tar warning; its clock was not changed and app behavior does not depend on that clock.

Not established: session launchability, full KDE Wayland dependencies, GPU readiness,
installation, activation, compositor behavior, application/window preservation, broader
distribution compatibility or exhaustive absence of side effects.
