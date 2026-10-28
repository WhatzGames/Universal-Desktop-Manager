# Establish read-only v0.1 foundation and persistent project plan

## Problem and resulting behavior

The repository had only LICENSE and .gitignore. This Section 12 setup adds a one-member
Rust workspace and read-only headless Bevy ECS controller that reports host basics,
standard system session definitions and a KDE Plasma Wayland catalog entry as JSON.
Only Debian 13 queries local APT package candidates. Availability, session entry presence,
unverified launchability and live-switch capability are separate. No privileged changes.

Preserve the complete master plan verbatim and full phase roadmap. Add agent session
protocol, compact handoff, architecture/design/ADR, user Wiki source and initialization
instructions, contribution/security guidance, issue/PR templates and Linux CI. Existing
LICENSE and .gitignore are unchanged. No SPDX project license choice is inferred.

## Validation

Historical baseline Rust 1.97.1 on macOS aarch64: fresh detached checkout locked offline build, six tests,
formatting and Clippy with warnings denied passed. JSON report smoke test passed.
Linux Ubuntu CI passed all checks and report smoke test:
https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40770234918
GitHub confirms foundation commit c513695 has a valid Verified SSH signature.
Source master plan, LICENSE and .gitignore byte comparisons passed.

## GitHub handoff and blockers

My Flow bare/worktree layout, github-personal SSH transport, personal SSH signing and
attribution hook configured. Owner granted integration access; PR #1 and enhancement issues #2–#9 now exist.
No milestone creation tool is exposed; explicit approval is pending for temporary
issues:write automation. Publication instructions are included. Wiki is
enabled but uninitialized; user pages are ready to publish. miix320 SSH failed with
No route to host. No milestones exist yet.

## Scope, risks and next task

No GUI, package install, compositor, session activation or live switching. Standard
system session paths only, no executable/GPU readiness proof. APT metadata may be stale;
a synchronous query can stall if the local tool hangs. Real Debian 13 desktop validation
and distribution-license audit remain open. Next: publish tracking/Wiki with owner access
and validate discovery on Debian 13 before planning v0.2. Do not merge this PR.
