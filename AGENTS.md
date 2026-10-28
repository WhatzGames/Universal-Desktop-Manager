# Agent session protocol

At startup inspect `git status`, branch and remotes. Read PROJECT_STATE.md, the full
master plan, roadmap, relevant architecture/design docs and ADRs. Inspect the assigned
issue/milestone and existing code/tests before choosing a scoped task. Never rely on
chat memory or treat proposed functionality as implemented.

Work on a separate branch; preserve unrelated changes and LICENSE. Do not infer
project SPDX terms from the generic GPLv2 text. Do not merge without human approval.
Keep v0.1 read-only: no package refresh/install, root operations, logout, display-manager
restart, compositor takeover or execution of discovered desktop commands.

Before closeout run cargo fmt --check, cargo clippy --workspace --all-targets -- -D warnings,
cargo build --workspace --locked, cargo test --workspace --locked and a report smoke test.
Report acceptance criteria with evidence, failures and unverified claims. Update relevant
technical docs, issue/PR and PROJECT_STATE.md with verified state, blockers, next task
and validation commands. Handoff persistent artifacts, not a diary. CI does not prove
semantic compliance or real hardware compatibility.

Sources of truth: code/tests = behavior; docs/development/roadmap.md = roadmap;
Issues/Milestones = tasks; PROJECT_STATE.md = current handoff; accepted ADRs = decisions;
GitHub Wiki = end-user manual (publish-ready source in docs/wiki until initialized).
