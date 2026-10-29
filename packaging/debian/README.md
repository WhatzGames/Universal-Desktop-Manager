# Debian 13 package helper (v0.2 development)

Prerequisites on the disposable Debian 13 VM: system Python 3, `python3-apt`,
`polkitd` and `pkexec`. These are system dependencies, not pip dependencies.
Do not provision this helper on a primary desktop while VM acceptance is pending.

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

A [prepared VM review packet](../../docs/development/validation/v0.2-vm/README.md)
now records real XFCE/LightDM baseline and restored KVM/TCG snapshots. This is
preparation evidence only. Do not execute its install/failure stage until a human
approves the exact snapshot manifest and complete transaction digest.
