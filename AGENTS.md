# Development instructions

Inspect git status, branch, relevant code/tests, roadmap and architecture/design docs
before changing behavior. Work on a separate branch, preserve unrelated changes and
LICENSE, and do not merge without approval. Do not infer project SPDX terms from the
generic GPLv2 text. Keep discovery read-only: no package refresh/install, root actions,
logout, display-manager restart, compositor takeover or discovered-command execution.

All shipped UDM-owned application logic, including privileged helpers, must be Rust.
FFI to native libraries is allowed; bridge code only adapts types/calls. Adopt Rust
bindings only after verifying active maintenance, supported native-library versions
and meaningful tests. Do not silently substitute unsupported bindings, shell wrappers
or interpreter backends. Python development/CI/test tooling is separate.

Use native libraries/APIs and structured IPC for system operations. Never evaluate
application data through sh -c, bash -c, system(), shell=True or equivalent code/shell
evaluation. Preserve authentication, transaction validation, locking and recovery
semantics when changing integration. CI/build/test automation has a separate purpose.

Run cargo fmt --check, cargo clippy --workspace --all-targets --locked -- -D warnings,
cargo build --workspace --locked, cargo test --workspace --locked and a report smoke
test before closeout. Keep documentation focused on product behavior, architecture,
usage and testing. Update user-facing Wiki source when product behavior changes.

Do not commit agent diaries, gap inventories, session summaries, conversation-derived
records or handoff/status files. Do not commit CI run outputs, logs, screenshots,
VM manifests/snapshots or copied artifact reports; keep them in Actions artifacts.
Keep authored test fixtures separate from run outputs. Communicate work status in the conversation and
relevant issue/PR. Code/tests define behavior; roadmap defines planned scope; issues
track tasks; architecture/design documents define technical contracts.
