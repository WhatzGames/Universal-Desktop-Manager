# UDM technical roadmap

Source: [complete master plan](master-plan.md). These phases are plans, not release claims.


### v0.1 — Foundation and discovery

- Create Rust Cargo workspace, minimal Bevy headless app, shared types, ECS plugins, structured logs/config.
- Detect Linux OS/distribution/architecture and supported package manager, without privilege.
- Discover existing sessions from desktop/session definitions.
- Model desktop catalog including not-installed KDE Plasma Wayland.
- Do **read-only** KDE package availability/compatibility checks (where repository interface supports safely querying).
- Build automated unit tests and CI.
- Establish agent persistence, GitHub technical docs, end-user wiki skeleton, issues/milestones.
- **Acceptance:** `cargo build`, tests and formatting pass; app starts and generates honest read-only desktop/KDE status; no root actions, packages installed, or session manipulation.

### v0.2 — KDE installation

- Native distribution package adapter (one distro first), transaction simulation, dependency/conflict review.
- Privileged minimal helper + Polkit, authorized install, journal and failure handling.
- Verify KDE Plasma Wayland install and session launcher.
- **Acceptance:** install in snapshot VM after approval without disrupting current desktop; failed transaction reports recovery accurately.

### v0.3 — Native session activation

- Standard KDE Wayland login/session discovery and activation through supported mechanisms.
- Session compatibility model and clear preservation guarantees.
- **Acceptance:** native Plasma can be selected/launched through a supported path without pretending current windows migrated.

### v0.4 — Persistent Wayland compositor

- Smithay nested compositor based on maintained examples; XDG window management, focus/input, geometry/workspace, rendering.
- Bevy↔compositor typed event bridge.
- **Acceptance:** multiple native Wayland clients run and window registry reflects reality.

### v0.5 — Integrated live shells

- At least two switchable custom shells, e.g. GNOME-inspired and Plasma-inspired.
- Readiness handshake, transactional switch, preservation verification, rollback.
- **Acceptance:** browsers, terminals, editor apps remain connected and usable across repeated changes.

### v0.6 — X11 support and nested-session prototypes

- Xwayland and X11 WM integration, mixed X11/Wayland window-preservation tests.
- Begin isolated nested KWin/Plasma and X11 experiments.
- **Acceptance:** Xwayland clients remain functional across live shell changes; nested mode reports no migration guarantee.

### v0.7–v0.9 — Expand and harden

- Additional distributions/desktops, multi-monitor, graphics compatibility, suspend/resume, rollback/failure injection, profiling, security audit, packaging.
- **Acceptance:** documented version-by-version compatibility, tests in multiple environments, secure installer and reliable recovery.

### v1.0 — Stable release

- Ship only demonstrably tested features. Publish release notes, user wiki guidance, compatibility matrix, packaging and support/security policy.
- Native arbitrary GNOME↔KDE window migration remains research until independently proved; it is **not** a v1.0 promise.
