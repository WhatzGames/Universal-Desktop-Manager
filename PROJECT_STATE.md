# Current project state

Verified: 2026-10-28. Current phase: v0.1 foundation setup, pending PR review.
Branch: setup/v0.1-foundation. No release or merge has occurred.

Implemented: one-member Cargo workspace; exact Bevy 0.20 app/ECS dependencies;
read-only host/system-session discovery; KDE catalog; Debian 13 local APT candidate
query; structured JSON report; ECS startup plugin; six tests; CI; agent protocol;
full master plan copied verbatim and full phase roadmap; architecture/design/ADR;
contribution/security guides; issue/PR templates and publish-ready Wiki.

Verified locally on macOS aarch64 / Rust 1.97.1: formatting, Clippy with warnings denied,
locked build and six tests pass. Report starts without privilege and correctly reports
unsupported macOS package queries. LICENSE and .gitignore match main byte-for-byte;
master-plan.md matches the provided source. Fresh detached checkout also passed locked offline build, tests, formatting and Clippy.
Linux Ubuntu GitHub CI passed all steps (fmt, Clippy, locked build, six tests, report):
https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40770234918
Signed foundation commit c513695 is confirmed verified=true, reason=valid by GitHub:
https://github.com/WhatzGames/Universal-Desktop-Manager/commit/c513695
Published branch: https://github.com/WhatzGames/Universal-Desktop-Manager/tree/setup/v0.1-foundation
PR #1 is open and unmerged: https://github.com/WhatzGames/Universal-Desktop-Manager/pull/1
GitHub write access was granted by the owner; the earlier 403 is resolved.
Ready-to-submit description: docs/development/setup-pr.md.

Planned/unverified: real desktop-session host discovery and Debian 13 package query, executable
launchability, GPU support, package installation, UI, compositor, native sessions and
live shell switching. No preservation claims. Test host miix320 unreachable (No route
to host). Missing/unreadable definitions and stale metadata limits are documented.

GitHub tracking: eight open enhancement issues #2–#9 cover workspace, ECS, catalog,
distribution/session discovery, KDE compatibility, CI and docs. They link PR #1 and
verified validation. Milestones are not yet created: no connector tool; temporary
issues:write workflow rejected by automatic approval review, pending explicit approval.
Wiki enabled but uninitialized; browser signed out. Publish-ready source: docs/wiki.
Local gh account does not have owner write access. GitHub connector now does.
Rust upgrade: latest stable 1.99.1 is pinned in rust-toolchain.toml, manifest and CI;
formatting, Clippy with warnings denied, locked build, six tests and report smoke
test passed locally. Latest-toolchain Linux CI pending push. Earlier Rust 1.97.1
validation remains historical evidence. miix320 is internal-network-only; use its
existing SSH alias, never substitute a public endpoint.

Next: finish Rust 1.99.1 validation and PR checks, obtain approval for milestone
initialization or publish through an owner-authenticated browser/CLI, then validate
discovery on reachable Debian 13 Linux. Publish Wiki using documented owner steps. v0.2
installation requires a separate approved task and disposable VM. Do not merge here.
