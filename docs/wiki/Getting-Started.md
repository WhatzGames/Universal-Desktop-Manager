# Getting started

There are no packaged releases. The v0.1 foundation from
[PR #1](https://github.com/WhatzGames/Universal-Desktop-Manager/pull/1) is merged into
the main branch. v0.2 installation work is experimental and remains under development. With Git, rustup and a native linker on your development machine:

```sh
git clone https://github.com/WhatzGames/Universal-Desktop-Manager.git
cd Universal-Desktop-Manager
cargo run --locked -p udm-app
```

The checked-in toolchain file selects Rust 1.99.1. A first source build needs access
to that toolchain and its dependencies; an offline test host can use a transferred
build from the same source revision. See [First Launch](First-Launch) for the report.
Run as a regular user, without sudo. There is no graphical manager or switching yet.
Session entry presence does not establish that a desktop can launch.
