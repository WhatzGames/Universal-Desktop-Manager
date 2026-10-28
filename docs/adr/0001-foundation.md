# ADR 0001: read-only Rust/Bevy foundation

Status: accepted for this setup implementation; future runtime design remains proposed.
Date: 2026-10-28

Use Rust 2024 and exact Bevy app/ECS 0.20.0 pins, disabling default features and enabling
std. Bevy ECS requires Rust 1.95; this workspace requires and pins Rust 1.99.1, the latest stable verified 2026-10-28.
Cargo.lock fixes transitive resolution. The toolchain file and CI both pin 1.99.1 at the user’s request; repeat validation
when upgrading the pin. Historical baseline checks used 1.97.1.

Use one workspace member and module boundaries to avoid empty crates. JSON is both the
report and structured diagnostic output; defer configurable paths and persistent operation
storage until a workflow needs them. Bevy subcrates license themselves MIT OR Apache-2.0;
the project license choice and a distribution dependency audit remain unresolved.

Keep end-user guidance in the Wiki; technical specifications and agent handoff in Git.
Use one release-specific local APT query (Debian 13), explicitly unvalidated elsewhere.

Proposed, not accepted by implementation: Smithay/calloop runtime isolation, typed IPC,
Polkit helper and transaction/rollback preservation contract. These require focused ADRs
and experimental evidence before their implementation. Never infer arbitrary migration.

Sources: https://docs.rs/bevy_ecs/0.20.0/bevy_ecs/ and
https://docs.rs/bevy_app/0.20.0/bevy_app/ ; cargo info for pinned Rust requirements;
https://blog.rust-lang.org/releases/ for available stable Rust releases.
