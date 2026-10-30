# Universal Desktop Manager

Experimental Linux desktop discovery and future desktop management. v0.1 is a
headless, read-only Bevy ECS controller that prints a JSON report. It detects host
basics, standard system session entries and a KDE Plasma Wayland catalog item.
Only Debian 13 has a local APT candidate query; this does not prove installability.
Other distributions report unsupported package querying. Session entry presence does
not prove installation completeness or launchability. macOS runs report unsupported.

The v0.2 development branch adds an explicit Debian 13 KDE transaction CLI and restricted
Polkit helper. The approved Debian 13 snapshot-VM suite passed real installation,
documented failures, original desktop continuity, isolated Plasma and snapshot recovery.
This validates that disposable guest, not a supported release or physical hardware.
[Acceptance evidence](docs/development/validation/v0.2-vm/kvm-fixed/accepted/README.md). See [helper setup and limits](packaging/debian/README.md).
No GUI, compositor, session activation or live switching exists.
Arbitrary GNOME/KDE or Xorg/Wayland window migration is not promised. Future integrated
switching uses custom shells on one persistent compositor, not native GNOME/KDE shells.

## Build and run

Install Rust 1.99.1 (latest stable verified 2026-10-28; pinned by rust-toolchain.toml) with a native linker. From a clean checkout:

```sh
cargo build --workspace --locked
cargo run --locked -p udm-app
cargo fmt --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
```

Validation: [offline hardware and Debian evidence](docs/development/validation/README.md),
[testing procedure](docs/development/testing.md).

The default report needs no sudo. Explicit package installation requires Polkit administrator authorization. JSON stdout contains a schema version, host, sessions, desktops and
warnings. Failures reading existing definitions or executing the supported query return
nonzero; missing session directories are normal. No configuration file is needed yet.

[User Wiki](https://github.com/WhatzGames/Universal-Desktop-Manager/wiki) ·
[Wiki source / publication](docs/wiki/README.md) ·
[Technical architecture](docs/architecture/overview.md) ·
[Full master plan](docs/development/master-plan.md) ·
[Roadmap](docs/development/roadmap.md)

The existing [LICENSE](LICENSE) is unchanged. Project-level SPDX choice remains open;
packages are not configured for registry publication.
