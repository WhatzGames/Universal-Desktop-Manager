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
and a 1280x800 screenshot whose desktop background is non-blank. A known installed
Breeze wallpaper is configured through Plasma's scripting API; the image check excludes
the panel so clock text alone cannot satisfy it. The seven-day `plasma-wayland-smoke` artifact
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
CachyOS hardware cannot validate the release-specific APT adapter. Report results in the relevant issue/PR, distinguishing observed from planned.

## v0.2 package workflow

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/packages -v`
for safety, journal and injected-failure tests without root or APT. The separate
Debian CI job provisions python3-apt in a disposable container and runs
`tests/packages/debian-simulation.sh` as nobody. It checks repeated native resolution,
no removal/upgrade/display-manager additions, honest pre-install verification and
identical before/after package inventory. It never installs KDE.

Each real
installation requires a newly reviewed VM-specific plan and explicit approval.

## Snapshot VM CI candidate

[Real VM protocol, approval gate and limits](../../tests/vm/README.md). Preparation
and acceptance are separate operations; the existing container job remains
a fast component check. Real guest preparation/restore and default Polkit denial passed on hosted KVM
and TCG; review artifacts are retained by the corresponding Actions run.
The approved KVM suite passed real KDE commit, documented failure/interruption,
desktop continuity, isolated Plasma and final recovery in run 40975763374.
[Acceptance run](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40975763374); [protocol limits](../../tests/vm/README.md).
Keep issue #11 and milestone v0.2 open for review/merge.

## Push approval filtering

[Strict signed single-file approval gate](../../.ci/README.md).
Denial and non-trigger results belong to their Actions runs.
Ordinary integration pushes skip VM preparation; `[vm-prepare] ` opts in explicitly.
Only a separate exact approved record can schedule installation. The expected false-record workflow failure is a denial test; the subsequent exact
human-approved native acceptance passed. Reruns and semantic approval repeats remain
rejected; no further installation is authorized by an ordinary documentation push.

## Retrieving CI results

Keep test source and small authored fixtures in Git. Run outputs—logs, screenshots,
reports, package plans, VM manifests/snapshots and image inventories—belong in Actions
logs/artifacts. Do not copy them into docs or turn captured runs into test fixtures.
Tests should construct synthetic cases where deterministic input is required.

```sh
gh run list --repo WhatzGames/Universal-Desktop-Manager
gh run view RUN_ID --repo WhatzGames/Universal-Desktop-Manager --log
gh run download RUN_ID --repo WhatzGames/Universal-Desktop-Manager --dir target/ci-artifacts/RUN_ID
```

Select a named artifact with --name when only a review packet or image is needed.
Current workflows retain uploaded artifacts for seven days; logs follow the
repository's GitHub retention settings. Expiry can make outputs unavailable.
Review-dependent installation must stop when required artifacts are missing; run
fresh preparation and obtain exact approval rather than bypassing integrity checks.
