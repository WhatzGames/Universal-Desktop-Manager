# Current project state

Verified baseline: 2026-10-28. Integration work started: 2026-10-29. Active milestone: v0.2 — KDE installation, Debian 13 only.
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
[Draft PR #13](https://github.com/WhatzGames/Universal-Desktop-Manager/pull/13) is open.
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
16 Python safety/injected-failure tests and default report smoke test pass.
Native Debian 13 ARM64 simulation as UID 65534: repeated plans identical, package
inventory unchanged; 798 NEW packages, 364,910,796 download bytes and 1,455,311,872
installed bytes estimated, zero removals/upgrades/new display managers. Only test
prerequisite python3-apt was provisioned. KDE was NOT installed. Container removed.
GitHub push and PR CI both passed on bba56f1, including native Debian x86_64
simulation and the Linux report job:
https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40780259048
https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40780213650
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
Signed Wiki update f5bb5ac (following e0a3763) is published on master; all fourteen pages and sidebar
match docs/wiki source copies. It corrects merged-foundation status and distinguishes
simulation from unvalidated installation. GitHub confirms implementation commit
bba56f10f6428d88177d1213d4180a6763b06468 as Verified. Personal SSH signing and My Flow attribution hooks are retained.
GitHub CLI's credential has no repository push permission; connected GitHub API and
personal SSH transport are used for authorized repository updates. Branch protections
could not be read with the CLI credential (404); do not infer that none exist.

## Snapshot VM CI integration (in progress)

Separate branch `ci/debian13-snapshot-vm`, worktree
`/Users/obedkooijman/CodexProjects/worktrees/Universal-Desktop-Manager-snapshot-vm`.
Live PR #12 is MERGED as main 2ae133a; PR #13 remains draft at 67165a2.
The integration merges main into a child of that exact PR #13 head; its origin
security correction and both original branches remain intact. No PR is merged here.

`tests/vm/` and the manual Debian VM workflow are an implementation candidate:
real QEMU Debian XFCE/LightDM guest, running RAM/disk snapshot, exact transaction
review artifacts, separate digest-bound human approval, real pkexec/helper path,
snapshot-isolated success/failure cases and independent Plasma component verification.
See tests/vm/README.md for the precise gate, evidence and limits. New preparation
and native acceptance evidence are still pending; no unseen transaction is approved.
Local macOS fmt, Clippy, locked build/test (7 Rust tests), report smoke and all 16
helper tests pass. Two new approval-boundary tests pass. Official stable Rust manifest
was fetched on 2026-10-29 and reports 1.99.1; pins remain unchanged.
Container-scoped Debian QEMU tooling builds; no host packages were installed.

Draft integration PR: https://github.com/WhatzGames/Universal-Desktop-Manager/pull/14
(targets PR #13's branch; no merge). Published source 32904de is GitHub Verified.
The new workflow is not on default main, so the existing CI workflow calls it;
scoped integration-branch pushes can prepare only. Accept remains a separate
explicit digest-bound workflow_dispatch. CLI dispatch lacks repository admin rights;
no permission expansion was attempted. Hosted preparation run 40949359230 is in
progress; it is not installation acceptance. Published Wiki commit bb46dc8 updates
the two user-facing approval/limitation pages and matches reviewed source copies.
