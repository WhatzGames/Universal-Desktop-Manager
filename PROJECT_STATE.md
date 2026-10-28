# Current project state

Verified: 2026-10-28. Active milestone: v0.2 — KDE installation, Debian 13 only.
This chat's persistent goal continues after v0.1; installation acceptance is not complete.

## Base and work

PR #1 is MERGED (live GitHub check), squash main
`3bca2623e3cabf15bc8341f2d060aa482aceed15`. Foundation issues #2–#9 are closed.
The original setup worktree/branch remains untouched.
v0.2 branch: `feature/v0.2-debian-kde`, separate worktree
`/Users/obedkooijman/CodexProjects/worktrees/Universal-Desktop-Manager-v0.2-kde`.
Issues: [implementation #10](https://github.com/WhatzGames/Universal-Desktop-Manager/issues/10),
[VM acceptance #11](https://github.com/WhatzGames/Universal-Desktop-Manager/issues/11),
[milestone v0.2](https://github.com/WhatzGames/Universal-Desktop-Manager/milestone/2).
Keep the v0.2 PR unmerged; no release or v0.3 session activation.

## Implemented candidate

Default Rust/Bevy discovery remains read-only. Explicit package CLI dispatches to a
restricted root-owned isolated-Python helper backed by Debian's native python3-apt.
Fixed KDE targets; resolution, full transaction review JSON, origin/version/dependency/
conflict/size metadata; SHA-256-bound review and locked re-resolution; Polkit admin
authorization; no UI commands/paths/package names; no repository additions or refresh.
All removals/upgrades/reinstalls and new display managers are rejected. Temporary
exclusive service-start policy preserves existing administrator policy by refusing it.
Durable atomic/fsynced operation records distinguish failure/interruption from ready;
manual native recovery guidance, no automatic rollback. Verify actual target packages,
clean dpkg audit, launcher and Debian wrapped Wayland session definition. GPU readiness
remains unverified. No session is started or switched.

Design/limits: docs/design/installation.md, docs/adr/0002-debian-installation.md and
packaging/debian/README.md. Existing LICENSE, .gitignore and master-plan.md unchanged.

## Verified evidence

Official stable Rust manifest still reports 1.99.1, matching toolchain/manifest/CI.
macOS ARM64 fmt, warning-free Clippy, locked workspace build/tests (7 Rust tests),
15 Python safety/injected-failure tests and default report smoke test pass.
Native Debian 13 ARM64 simulation as UID 65534: repeated plans identical, package
inventory unchanged; 798 NEW packages, 364,910,796 download bytes and 1,455,311,872
installed bytes estimated, zero removals/upgrades/new display managers. Only test
prerequisite python3-apt was provisioned. KDE was NOT installed. Container removed.
Full evidence, digest, image identity, before/after inventories and limitations:
docs/development/validation/v0.2/. Separate CI job repeats unprivileged simulation.

## Acceptance blocker and next action

No disposable Debian 13 desktop VM with snapshots is configured. Podman's appliance
and Debian container are not installation acceptance environments. Actual KDE install,
Polkit prompt/denial, real dpkg/download interruption recovery and preservation of an
existing graphical session/display manager remain UNVERIFIED. Maintainer scripts run
as root; policy-rc.d is not a sandbox. Do not use on the user's primary desktop.

Next: provide a disposable Debian 13 desktop VM, snapshot it, record original session
and display manager, provision reviewed helper prerequisites, generate a VM-specific
plan and present its exact transaction for explicit installation approval. The saved
container plan is review evidence, not authorization for another machine. Keep #11
and milestone open until real success/failure acceptance evidence exists.

miix320 is LAN-only, offline CachyOS, not Debian. It was not used for this milestone;
never enable its internet or use it for Debian installation testing.

## Documentation/publication

Fourteen-page Wiki existed at signed commit ee09dc3f040e119c8e0c00c600bf97ed42455c67.
v0.2 source updates correct merged-foundation status and distinguish simulation from
unvalidated installation. Keep the managed Wiki checkout synchronized and record its
publication revision. Personal SSH signing and My Flow attribution hooks are retained.
GitHub CLI's credential has no repository push permission; connected GitHub API and
personal SSH transport are used for authorized repository updates. Branch protections
could not be read with the CLI credential (404); do not infer that none exist.
