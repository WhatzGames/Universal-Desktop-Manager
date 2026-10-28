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

Current Rust 1.99.1 on macOS aarch64: fresh detached checkout locked offline build, six tests,
formatting and Clippy with warnings denied passed. JSON report smoke test passed.
Linux Ubuntu CI passed all checks and report smoke test:
https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40770234918
GitHub confirms foundation commit c513695 has a valid Verified SSH signature.
Source master plan, LICENSE and .gitignore byte comparisons passed.

## GitHub handoff and blockers

My Flow bare/worktree layout, github-personal SSH transport, personal SSH signing and
attribution hook configured. Owner granted integration access; PR #1 and enhancement issues #2–#9 now exist.
Milestones v0.1 through v1.0 were created using an explicitly approved temporary
issues:write workflow, then the workflow was removed. Issues and PR belong to v0.1. Wiki is
enabled but uninitialized; user pages are ready to publish. Offline miix320 inventory test now passes as UID 1000; sanitized reports and limits
are in docs/development/validation. All eight milestones exist; see github-management.md.

## Scope, risks and next task

No GUI, package install, compositor, session activation or live switching. Standard
system session paths only, no executable/GPU readiness proof. APT metadata may be stale;
a synchronous query can stall if the local tool hangs. Debian 13 container query execution passed; full desktop/graphics compatibility
and distribution-license audit remain open. Next: publish Wiki using documented owner steps
and validate discovery on Debian 13 before planning v0.2. Do not merge this PR.
