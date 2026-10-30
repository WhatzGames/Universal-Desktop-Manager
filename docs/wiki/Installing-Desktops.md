# Installing desktops

The v0.2 development branch provides an experimental Debian 13 KDE installation
workflow. It is not a supported release. The approved disposable Debian 13 VM suite
passed installation and original desktop continuity. See the scoped evidence below.
Do not try this experimental helper on your primary desktop.

The explicit `udm-app packages plan` command shows every proposed package and version,
its trusted Debian source, dependency/conflict information and size estimates.
It does not download or install KDE. UDM never adds repositories or refreshes metadata.
Only new packages are allowed; removals, upgrades and display-manager additions are rejected.

A separately provisioned helper is required. After reviewing the complete plan,
an approved test installation uses `udm-app packages install REVIEWED_SHA256` and
asks for administrator authorization. Any change to the reviewed transaction
requires a new review. Package installation does not select or start Plasma.

`udm-app packages verify` checks installed KDE packages, launcher and session entry.
A successful check does not establish graphics readiness or live switching.
See [Troubleshooting](Troubleshooting) for failures and recovery limits.

The [approved Debian 13 KVM test suite](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40975763374) passed real installation,
documented stale/download/dpkg/interruption/verification failures, original
XFCE/LightDM process and session continuity, isolated KWin/Plasma rendering and final
snapshot recovery. It added exactly 579 reviewed packages without removing packages
or changing existing versions. This validates the disposable test guest, not a
supported release or physical hardware. Ordinary pushes cannot trigger installation.

Each new transaction still requires review and explicit approval. GitHub execution
uses one signed approval-only push bound to the source, preparation run, manifest
and complete transaction; unrelated pushes and workflow reruns cannot install.
Interactive administrator password prompting, native package repair and physical
GPU/input remain unvalidated. Recovery in the suite restores the reviewed snapshot.
