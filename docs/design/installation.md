# Debian 13 installation contract (v0.2 candidate)

The no-argument report preserves v0.1's read-only behavior. Explicit `packages plan`,
`packages verify` and `packages install SHA256` dispatch to an installed absolute helper;
only install goes through `/usr/bin/pkexec`. Discovery never triggers authorization.
The controller remains a one-shot headless CLI; interactive GUI work is out of scope.

Lifecycle: host/repository checks → native dependency resolution → JSON simulation →
human review → Polkit authorization → locked re-resolution/digest comparison → durable
installing record → native commit → package/launcher/session verification → ready.
Failures retain error/recovery advice. Interrupted installing/verifying records block
retry. Preflight errors do not imply a package mutation or require blind repair.

Plan includes exact new-package names, architectures, versions, origins, dependency,
conflict/break/replace metadata, download bytes and installed-size estimates. These
are metadata estimates, not filesystem reservation or a guarantee that files will fit.
The entire plan plus dpkg/source/index/config/display-manager fingerprints is hashed.
Any changed plan is refused. Every removal/upgrade/reinstall, unknown origin and new
display manager is refused; recommendations/suggestions are disabled. Native APT checks
signed metadata and package hashes, and unauthenticated downloads are explicitly disabled.
The helper never updates metadata, adds repositories or accepts arbitrary commands.

Service starts/restarts are suppressed by an exclusively created policy-rc.d; an
existing policy causes failure without replacement. NEEDRESTART_MODE=l prevents
needrestart from requesting service restart. No session/logout/display-manager command
is called. Maintainer scripts remain root code, not sandboxed. Therefore current desktop
preservation remains a VM acceptance requirement, not a consequence proved by unit tests.
A crash can leave the guard in place; recovery instructions explicitly require inspection.

Verification requires all seven target packages, clean dpkg audit, executable
startplasma-wayland and a compatible Wayland desktop entry (including Debian's D-Bus
wrapper). It reports reboot-required marker, GPU readiness unverified, no session started
and live-switch false. Qt dependencies come from native Plasma resolution. No v0.3 activation.

Records: root-only `/var/lib/udm/operations`, one flock-serialized operation, unique IDs,
JSON atomic replacement with file and directory fsync. No automatic rollback or repair.
APT/dpkg logs supplement operation records. A failed commit may leave installed or
unconfigured packages; administrator recovery or a VM snapshot is the fallback.

[Deployment and CLI](../../packaging/debian/README.md) · [ADR](../adr/0002-debian-installation.md)
