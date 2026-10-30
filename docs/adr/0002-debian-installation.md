# ADR 0002: restricted Debian 13 installation transactions

Status: implemented candidate; approved disposable snapshot-VM suite passed.
Date: 2026-10-28

The user clarified the [library-first/no-shell requirement](../design/process-execution.md)
on 2026-10-30. This ADR describes the existing helper boundary; fixed CLI/helper
process calls are documented gaps against that preferred integration, not permission
for shell operations or arbitrary commands. Retain native APT bindings and preserve
privilege/audit semantics when replacing the remaining process-based interfaces.

Keep discovery in the Rust/Bevy application. Use Debian's system `python3-apt`
binding to its native APT resolver and commit implementation, avoiding a new Rust
FFI layer or parsing human apt-get output. A root-owned isolated Python executable
is the separate privilege boundary. It accepts fixed `plan`, `verify`, and
`install REVIEW_DIGEST` operations only. Rust invokes absolute helper/pkexec paths
without a shell. No package names, arbitrary paths, options or commands come from UI.

Polkit authenticates an active user's administrator authorization without cached
permission. The helper binds authorization to a recomputed plan using SHA-256 and
holds the APT system lock across re-resolution/commit. JSON operation records use
fsync plus atomic replacement; interrupted changes require administrator review.
SQLite is unnecessary for one serialized package operation at a time.

Conservative first scope: reject all removals/upgrades/reinstalls, unknown origins,
and additional display managers; disable recommendations. This can refuse otherwise
valid installs rather than risk an unreviewed system or graphics change. Do not
expand this policy until concrete transactions demonstrate the need.

A temporary exclusive policy-rc.d suppresses service starts/restarts. Existing
administrator policies are preserved by refusing to proceed. This is not a
maintainer-script sandbox. Desktop/session preservation must still be tested in a
snapshot VM. No rollback claim: partial dpkg state requires native recovery or VM
restoration. No native session activation or shell switching is implemented.

Sources: [python-apt cache API](https://apt-team.pages.debian.net/python-apt/library/apt.cache.html),
[APT locking](https://apt-team.pages.debian.net/python-apt/library/apt_pkg.html#locking),
[Debian 13 KDE metapackage](https://packages.debian.org/trixie/kde-plasma-desktop),
[Plasma workspace](https://packages.debian.org/trixie/plasma-workspace).

CI integration candidate: preserve RAM/disk and exact source/transaction in review
artifacts, then require a separate digest-bound explicit approval before any KDE
commit. Revalidate snapshot files, original desktop identities and guest transaction.
See [protocol and remaining acceptance limits](../../tests/vm/README.md).

The [approved KVM acceptance](../development/validation/v0.2-vm/kvm-fixed/accepted/README.md)
passed real CLI/pkexec/helper installation, native failures/interruption, original
XFCE/LightDM continuity, isolated Plasma and final snapshot recovery. The original
host-bound KVM snapshot was withdrawn; a fixed enforced CPU model passed independent
restoration. Interactive password prompting, native repair and physical hardware
remain unvalidated. This is scoped disposable-guest evidence, not general safety.

A narrowly filtered push can carry the same explicit approval: one signed owner
commit changes only the dedicated approval record and names its exact manifest.
Approval-commit identity is distinct from the frozen guest source; both are checked.
No active approval is bundled with this mechanism. See [.ci/README.md](../../.ci/README.md).
