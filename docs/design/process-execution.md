# Library-first application runtime; no shell-command evaluation

User requirement, 2026-10-30: perform desktop/package/system operations through
maintained libraries, native APIs or structured IPC. Do not implement application
operations by constructing and evaluating shell commands. Prefer official package
manager bindings over invoking CLI tools and parsing their human-readable output.

The runtime must not invoke `sh -c`, `bash -c`, `system()`, `shell=True` or equivalent
shell/code evaluation. User input, package metadata, session definitions, catalog
entries and configuration must remain data, never command strings or arbitrary
executable paths. Quoting/escaping is not a substitute for this boundary. Do not
execute discovered desktop-entry `Exec` values as a shortcut to session activation.

Use APT's `libapt-pkg`/`libapt-inst` developer interfaces or maintained bindings;
the required shipped implementation is Rust, including the privileged helper.
The current installer uses Debian's `python3-apt` for resolution and commit, which
is library-backed but does not meet the Rust runtime requirement. Replace that
backend with Rust native-library integration while preserving its safety contract.
FFI is explicitly allowed. Keep UDM-owned policy, workflow and safety logic in Rust;
foreign bridge code only adapts types/calls into external native libraries.
Use structured system-service interfaces for future session/authorization operations.
The privileged helper must remain narrow and separately authorized, regardless of
which library/interface performs the work. Native bindings require validation and
safe memory/lifetime handling too; library use is not a guarantee against all RCE.

## Current implementation inventory

| Operation | Current implementation | Requirement status |
|---|---|---|
| Package resolution/download/commit | `python3-apt` (`apt`, `apt_pkg`) | Library-backed but Python; migrate helper to Rust and preserve native APT/safety semantics |
| Read-only availability query | Fixed `/usr/bin/apt-cache policy kde-plasma-desktop` in `compat.rs` | Direct process, no shell; remaining CLI-wrapper migration |
| Package audit | Fixed `/usr/bin/dpkg --audit` in the helper | Direct process, no shell; investigate supported library equivalent without weakening audit semantics |
| Helper and administrator authorization | Fixed absolute helper path and `/usr/bin/pkexec`, separate arguments and validated digest | Direct processes, no shell; review API/structured IPC replacement as part of privilege-boundary design |
| Temporary service-start guard | Generated fixed `policy-rc.d` shell script invoked by package-service tooling | Remaining UDM-owned interpreter boundary; migrate to a reviewed non-shell guard while preserving service suppression |

These existing process launches are documented implementation gaps, not permission
to add general command execution. Replacing a privilege boundary or audit must retain
authentication, transaction binding, locking, recovery and existing failure checks.
Do not remove safety checks merely to eliminate a subprocess. Any remaining required
process boundary needs an explicit design justification and fixed executable/typed
arguments, never a shell string or a UI-selected program.

## What this does and does not promise

Calling an absolute executable with an argument vector does not itself invoke a
shell. Nevertheless, the desired integration is library/API-first. Audit new runtime
process calls rather than assuming every subprocess is either shell execution or safe.

Debian package installation inherently delegates to dpkg, package hooks and maintainer
scripts, which can themselves use interpreters and execute privileged code. UDM cannot
promise that installing normal Debian packages executes no shell anywhere. Keep trusted
origins, signed-package verification, explicit exact-transaction review, narrow privilege
and honest recovery limits. The fixed temporary policy-rc.d guard is also a package-service
integration script; it is not command evaluation of user input or a script sandbox.

This requirement applies to the shipped application/helper. Build scripts, Dockerfiles,
CI and disposable test harnesses have a different execution purpose; their use of shell
automation does not authorize shell-backed product operations.

This inventory is a source check, not a complete security audit. No runtime behavior
was changed or additional installation authorized by recording the requirement.

References: [APT development interfaces](https://packages.debian.org/trixie/libapt-pkg-dev),
[python-apt cache/commit API](https://apt-team.pages.debian.net/python-apt/library/apt.cache.html),
[Rust process arguments](https://doc.rust-lang.org/std/process/struct.Command.html),
[Debian maintainer-script contract](https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html).
