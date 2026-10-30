# Agent session protocol

At startup inspect `git status`, branch and remotes. Read PROJECT_STATE.md, the full
master plan, roadmap, relevant architecture/design docs and ADRs. Inspect the assigned
issue/milestone and existing code/tests before choosing a scoped task. Never rely on
chat memory or treat proposed functionality as implemented.

Work on a separate branch; preserve unrelated changes and LICENSE. Do not infer
project SPDX terms from the generic GPLv2 text. Do not merge without human approval.
Keep v0.1 read-only: no package refresh/install, root operations, logout, display-manager
restart, compositor takeover or execution of discovered desktop commands.

All shipped UDM-owned runtime components, including privileged package helpers, must
be written in Rust. The existing Python helper is legacy migration work, not an
approved target architecture. Python may remain in development/CI/test tooling.
FFI to system libraries is explicitly allowed. Keep all UDM-owned application logic
in Rust; foreign bridge code may marshal types/calls, not implement UDM policy.
Do not replace native bindings with shell wrappers or embedded interpreter backends.

Application runtime is library/API-first: use native libraries/bindings and structured
IPC, not shell command evaluation or new CLI-output wrappers. Never route data through
`sh -c`, `bash -c`, `system()`, `shell=True`, dynamic code evaluation or user-selected
executables. Existing fixed process calls are documented gaps, not general permission.
Preserve authorization/audit semantics when replacing them. Read
docs/design/process-execution.md before changing system integration. CI/build/test
shell automation is separate from shipped application operations.

Before closeout run cargo fmt --check, cargo clippy --workspace --all-targets -- -D warnings,
cargo build --workspace --locked, cargo test --workspace --locked and a report smoke test.
Report acceptance criteria with evidence, failures and unverified claims. Update relevant
technical docs, issue/PR and PROJECT_STATE.md with verified state, blockers, next task
and validation commands. Handoff persistent artifacts, not a diary. CI does not prove
semantic compliance or real hardware compatibility.

Sources of truth: code/tests = behavior; docs/development/roadmap.md = roadmap;
Issues/Milestones = tasks; PROJECT_STATE.md = current handoff; accepted ADRs = decisions;
GitHub Wiki = published end-user manual; reviewed source copies and publication procedure
in docs/wiki. Keep those copies synchronized for authorized manual updates.
