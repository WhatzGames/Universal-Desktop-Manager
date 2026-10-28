# Foundation validation

Use the pinned Rust 1.99.1 toolchain and the README commands for formatting, Clippy,
locked build, tests and a JSON report smoke test. These are read-only application tests;
there is no compositor, installer or session activation to test yet.

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

## Real Plasma component smoke test in PR CI

The `plasma-wayland-smoke` PR job builds a disposable Debian 13 image from trusted
APT packages. It runs real KWin Wayland with its X11 windowed backend inside Xvfb,
then starts plasmashell. KWin QPainter and Qt Quick software rendering run without a
DRM device; the desktop runs
as UID 1000 with a private D-Bus session and no runtime network, host display or devices.
The CI image build installs test dependencies only inside the container, not on miix320.
It clears KWin's packaged realtime scheduling file capability so execution fits Docker's
default capability bound; no container capability is added. Production realtime scheduling
is outside this test's scope.

Bounded checks require the Wayland socket, a responsive Plasma scripting API reporting
at least one desktop and panel, active Wayland QPainter compositing, live processes
and a non-blank 1280x800 screenshot. The seven-day `plasma-wayland-smoke` artifact
contains the screenshot, process logs, KWin support information and JSON result. Process
exit or timeout fails the job; the workflow still copies diagnostics from the container.

To reproduce with a working Docker runtime, from the repository root:

```sh
docker build -t udm-plasma-smoke tests/plasma
docker create --name udm-plasma-smoke --network none udm-plasma-smoke
docker start --attach udm-plasma-smoke
docker cp udm-plasma-smoke:/tmp/plasma-artifacts plasma-artifacts
docker rm udm-plasma-smoke
```

This tests real compositor/shell startup and software-rendered output. It does not
start the full login service stack or test UDM installation, Polkit, display-manager
preservation, physical GPU/input, or seamless switching. Those require separate
integration and disposable-VM/hardware validation. Upstream backend options:
https://github.com/KDE/kwin/blob/v6.3.6/src/main_wayland.cpp

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
