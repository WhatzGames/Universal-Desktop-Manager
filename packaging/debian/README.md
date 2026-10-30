# Debian 13 package helper (v0.2 development)

This page describes the existing Python-backed candidate. The required product
architecture is Rust for the application and privileged helper; the Python helper
is the current prototype. [Package-helper architecture](../../docs/adr/0002-debian-installation.md).
The commands below document current behavior, not completed Rust migration.

Prerequisites on the disposable Debian 13 VM: system Python 3, `python3-apt`,
`polkitd` and `pkexec`. These are system dependencies, not pip dependencies.
This remains experimental; the passing disposable VM suite is not primary-desktop support.

Build UDM using the pinned Rust toolchain. An administrator installs the reviewed
helper and policy, with root-owned parents and no group/world write permissions:

```sh
sudo install -D -o root -g root -m 0755 packaging/debian/udm_packages.py /usr/libexec/udm-packages
sudo install -D -o root -g root -m 0644 packaging/polkit/org.whatzgames.udm.install.policy /usr/share/polkit-1/actions/org.whatzgames.udm.install.policy
```

No setuid bit, system service or general command execution endpoint is used.
The helper's isolated system Python ignores user Python paths. Polkit authorizes
only the installed absolute executable and asks for administrator authentication
on every invocation. Inactive/remote users are denied by default. Root can always
bypass application policy; this does not defend against an existing root compromise.

```sh
udm-app packages plan > reviewed-plan.json
udm-app packages verify
# Only after the human reviews the complete plan and approves this VM transaction:
udm-app packages install SHA256_FROM_REVIEWED_PLAN
```

`plan` uses local metadata only; it never updates repositories. Refresh metadata
separately as an administrator when needed, then regenerate the plan. The digest
binds the complete plan and relevant package/source/display-manager state. APT
re-resolves under its system lock before committing. Changed plans are rejected.
Only Debian's trusted deb.debian.org/security.debian.org stable/trixie origins are
accepted; other mirrors are currently refused. No repository is added.

Only new packages are allowed. Every removal, reinstall/upgrade and new display
manager is rejected. Recommendations are disabled to avoid SDDM. Existing service
policy is never overwritten: its presence blocks installation. A temporary
`policy-rc.d` denies service starts and restarts. Package maintainer scripts still
run as root, so this mechanism is not a sandbox or proof of desktop continuity.
Snapshot-VM testing with a running original desktop is mandatory before approval.

Durable records are root-readable in `/var/lib/udm/operations/*.json`. They retain
reviewed plan, authenticated caller UID, phase, verification and error/recovery advice.
APT/dpkg logs provide native details. `installing` or `verifying` left by a crash
blocks retries. An administrator must inspect APT/dpkg state and the UDM service
guard before resolving the interrupted record. Do not blindly delete records,
uninstall dependencies, downgrade or automatically rerun repair commands.

Verification checks the installed target packages, executable launcher and a
matching Wayland session definition. It does not start a session or establish GPU
readiness. Installation and v0.3 session activation remain separate.

VM preparation uploads its full package plan, manifest, original desktop captures
and snapshot as GitHub Actions artifacts. Review those artifacts before approving
an exact transaction. Installation/failure logs stay with the run; retrieve them
with gh run view or gh run download. Do not commit run outputs to the repository.
Interactive password prompting, native repair and physical hardware require separate
validation. Every new transaction still requires exact human approval.
