# ADR 0002: restricted Debian 13 installation transactions

Status: proposed Rust backend; the current prototype helper uses Python APT bindings.

UDM-owned application logic, including the privileged helper, is Rust. Use maintained
Rust bindings to native APT. Verify maintainer activity, compatibility with supported
Debian/APT versions, test coverage and security/ABI handling before selecting bindings.
No package is approved merely because it is available. Do not substitute a custom
resolver or shell/CLI wrappers for native package-management APIs.

FFI is allowed. UDM policy, validation, authorization, workflow, journaling and recovery
stay in Rust; foreign bridge code only adapts calls/types. External libraries retain
their native implementation. Review ownership/lifetimes and error propagation.

The package helper is a narrow, separately authorized privilege boundary accepting
fixed plan, verify and install REVIEW_DIGEST operations. Package names, arbitrary
paths, options and commands must not come directly from UI. The existing prototype
uses a root-owned isolated Python helper and fixed helper/pkexec paths without shell
command evaluation. Its observed behavior is documented in packaging/debian/README.md.

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

Integration runs publish logs and review/acceptance artifacts through GitHub Actions.
The VM protocol checks native installation/failure/recovery and desktop continuity;
interactive password prompting, native repair and physical hardware require separate
validation. A changed helper requires fresh native verification and exact transaction
approval. Historical runs do not establish correctness of a replacement backend.

Binding API reference: [rust-apt/libapt-pkg](https://docs.rs/rust-apt/latest/rust_apt/).
Native APT handles dependency resolution; adoption still requires compatibility,
maintenance and safety review.

A narrowly filtered push can carry the same explicit approval: one signed owner
commit changes only the dedicated approval record and names its exact manifest.
Approval-commit identity is distinct from the frozen guest source; both are checked.
No active approval is bundled with this mechanism. See [.ci/README.md](../../.ci/README.md).
