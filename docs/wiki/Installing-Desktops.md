# Installing desktops

The v0.2 development branch provides an experimental Debian 13 KDE installation
workflow. It is not a supported release. A disposable container has exercised
native dependency resolution; installation in a snapshot VM and preservation of
an existing desktop have not yet been validated. Do not try it on your primary desktop.

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

A separate snapshot-VM CI candidate is being developed. Its preparation stage
records the original desktop and exact package transaction. Installation requires
a separate explicit approval tied to that snapshot, source revision and transaction
digest. Passing the existing Plasma container check does not validate installation
safety, interactive authorization or preservation of your current desktop.
