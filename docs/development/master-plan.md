# Universal Desktop Manager — Master Project Plan and Agent Handoff

**Repository:** https://github.com/WhatzGames/Universal-Desktop-Manager  
**Project:** Universal Desktop Manager (UDM)  
**Document role:** Persistent development plan and initial repository-setup task specification  
**Status:** Proposed architecture and implementation roadmap; not evidence of implemented functionality  
**Prepared:** 2026-10-27

> **Instructions to the next Work/coding-agent session:** Read this entire document before editing the repository. Inspect the live repository before drawing conclusions about existing files, branch status, licensing, or GitHub Wiki availability. Preserve existing changes. Create a branch and a pull request; do not merge without approval. Do the initial setup described in Section 12, not the entire product implementation. Do not treat proposed designs as tested capabilities.

## 1. Vision and requirements

UDM is a Linux application for discovering, installing, configuring, and switching between desktop environments, including KDE Plasma, GNOME, XFCE, Cinnamon, and others. Users should be able to select an environment even when it has not yet been installed. UDM must support the ecosystem of X11 and Wayland, and prioritize preserving running application windows and user sessions.

### Required outcomes

1. Discover installed desktop sessions and identify additional desktop environments available from a distribution's trusted repositories.
2. Display available desktop environments in a graphical manager, with accurate installation and compatibility status.
3. Preview and, after explicit authorization, install missing environments using the system package manager.
4. Support native Wayland apps, X11 apps via Xwayland, and separately managed X11 or Wayland sessions where feasible.
5. Offer live desktop *shell* switching while the compositor and application display connections remain alive.
6. Support launching actual desktop environments (initially KDE Plasma Wayland), distinguishing native login, nested session, and integrated live-shell modes.
7. Track and validate application-process continuity, surface/connection continuity, focus, window placement, and workspaces for supported live switches.
8. Fail safely: never log the user out or kill the previous compositor as an implicit consequence of a supposedly seamless live switch.
9. Be extensible to additional desktop environments, distributions, and protocol backends.
10. Provide end-user documentation in the GitHub Wiki; maintain technical documentation and agent handoff state in the main Git repository.

## 2. Non-negotiable technical truth: three switching modes

**Mode A — Integrated live-shell switching (primary preservation MVP).** UDM owns a persistent compositor built with Smithay. Native Wayland application connections and the Xwayland server remain alive. UDM activates an alternative custom desktop shell (for example, GNOME-inspired or Plasma-inspired panels, launcher, dock and workspace presentation). Applications stay in the same compositor. This is a custom shell, **not** the genuine GNOME Shell or a full KDE Plasma session. Shell switches should be transaction-like with readiness checks and rollback.

**Mode B — Retained/nested native sessions (experimental).** Start a real environment such as KDE Plasma/KWin as a separate nested or isolated session. Keep the original display server/session alive and optionally return to it. Existing applications remain with their original session and do **not** migrate into the new desktop. Avoid two conflicting full graphical desktop service stacks in one user's shared systemd/D-Bus namespace; use tested isolation mechanisms.

**Mode C — Standard native login-session activation.** Use supported display-manager/session mechanisms to launch real KDE Plasma and other native desktop environments. This may require login/logout and **does not** promise preservation of windows across session termination. Do not label it as a live migration.

**Fundamental limitation:** Arbitrary native Xorg ↔ Wayland compositor handover, or moving all live windows from stock GNOME into stock KDE Plasma/KWin, is not universally supported. Xwayland lets X11 apps operate within a Wayland host; it is not a mechanism for magically migrating live Xorg windows to native Wayland connections. Bevy ECS alone cannot change this. Experimental reconnect/session restoration may become a future research track, with explicit compatibility limits. Never claim that installing Plasma makes its native shell live-switchable.

## 3. Architectural foundations

- **Language:** Rust.
- **Control plane:** Bevy ECS (Bevy may run headless; graphical UI eventually Bevy UI, subject to practical validation).
- **Display/compositor runtime:** Smithay with its own calloop-driven event loop, initially run nested for safety.
- **X11 compatibility:** Xwayland plus the appropriate X11 window-management implementation.
- **Native KDE compositor:** KWin in an actual, separately started KDE Plasma Wayland session or experimental nested session.
- **System services:** systemd/logind, D-Bus, Polkit, and native distribution package managers.
- **Configuration:** TOML for catalogs/manifests; SQLite for durable operation records when necessary.
- **Integration:** Typed IPC channels or authenticated local socket between Bevy control plane, compositor runtime, and privileged helper. Do not place live Wayland handles into ordinary ECS components or block the compositor while waiting for package operations.
- **Testing:** Cargo checks and automated unit/integration tests, nested Wayland sessions, disposable VMs with snapshots, then broader distributions/hardware.

### ECS model

| Entity class | Core components/data | Purpose |
|---|---|---|
| Desktop | ID, installed/available state, package manifest, supported backends, capabilities | Catalog and selection |
| Session | session ID, X11/Wayland backend, process references, lifecycle state | Real or nested graphical sessions |
| Window | compositor-owned stable ID mirrored to ECS, geometry, workspace, protocol, focus | Window continuity monitoring |
| Shell | shell ID, readiness, active/inactive state, compositor association | Interchangeable presentation |
| Installation operation | target, transaction ID, authorization and phase, progress/errors | Controlled package workflow |
| Switching operation | source/target, phase, preservation contract, rollback state | Safe transitions |

### Logical modules / Bevy plugins

`DesktopCatalogPlugin`, `CompatibilityPlugin`, `PackageManagerPlugin`, `InstallationPlugin`, `SessionManagerPlugin`, `WindowRegistryPlugin`, `ShellSwitcherPlugin`, `PreservationPlugin`, `RecoveryPlugin`, `DesktopUiPlugin`. Implement incrementally; do not create hollow crates or dummy public interfaces merely to match all future modules on day one.

### Process and security boundaries

1. **Unprivileged Bevy controller:** Owns ECS status and workflows; communicates via typed events/commands.
2. **Independent compositor:** Owns client sockets, input, rendering, and actual window surfaces; should continue functioning if management UI crashes.
3. **Restricted privileged package helper:** Accepts a tightly validated, pre-reviewed transaction, performs Polkit checks, invokes appropriate trusted package manager; never executes arbitrary UI-supplied shell commands. Avoid automatic repo additions or dangerous removals.

## 4. KDE Plasma Wayland: first real desktop integration

KDE is the first installation and native session target. KDE's *actual* packages do not provide an integrated shell for our own compositor; a separate Plasma-inspired shell adapter must be implemented for Mode A.

### Discovery and compatibility

- Read `/etc/os-release`, host architecture, available package manager, and package/repository metadata.
- Read `/usr/share/wayland-sessions/` and `/usr/share/xsessions/` (and other distro-specific discovery mechanisms where applicable).
- Inspect active session through `loginctl`/systemd when available; treat `XDG_SESSION_TYPE` and similar variables as advisory rather than definitive.
- Verify desktop-specific session entries, actual launcher executables, Wayland support, graphics capabilities, available storage, and system service/isolation constraints.
- Model `installed`, `available`, `unavailable`, and `unsupported` separately from `live-switch-capable`.
- Version package mapping per distribution/release instead of assuming universal package names.

### Package backends

Initial intended adapters: APT (Ubuntu/Debian), DNF (Fedora), pacman (Arch), Zypper (openSUSE). Implement and test **one distribution first**. Representative candidate metapackages/groups (verify per supported release and repository): Ubuntu `kubuntu-desktop`, Debian `kde-plasma-desktop` plus appropriate Wayland components, Fedora KDE desktop group, Arch `plasma-meta`, openSUSE KDE pattern. Let the native package manager resolve actual dependencies. Check KWin Wayland, Plasma workspace, Qt integration, Xwayland, desktop portals, Polkit agent, session launcher, and KScreen capabilities after installation.

### Safe installation lifecycle

`DISCOVER → CHECK_REPOSITORIES → RESOLVE → SIMULATE → REVIEW → AUTHORIZE → INSTALL → VERIFY → READY` (or a documented failure state). Show to users install/remove/upgrade sets, source repositories, download/disk estimates where available, important conflicts, and restart requirements. Explicitly block unreviewed removal of core system/graphics/display components. Preserve the original user session and display manager. An installation failure should surface package-manager recovery actions, not attempt a blind uninstall/downgrade.

### Activation policy

- Integrated live: available only with a tested custom shell adapter and stable host compositor; keep surfaces/connections.
- Nested native: real KWin/Plasma in an isolated environment; original apps stay in host, not migrated. This is experimental until validated.
- Standard native login: start Plasma through a supported login/session manager with honest notice about logout and window survival.
- Never automatically invoke logout as part of an operation advertised to preserve all windows.

## 5. Window preservation definition and testing

For a *supported integrated live-shell switch*, success requires:

- Same original app processes (verify PID **and** process start identity where possible).
- Same valid Wayland/X11 client connections and compositor/Xwayland instances.
- No destruction/recreation of application window surfaces because of the switch.
- Expected window geometry, workspace assignment, focus and input behavior retained (unless a user-directed layout change requires reflow).
- Windows responsive to keyboard/pointer after commit.
- Failed target shell starts cause rollback to previously functioning shell, without disconnecting apps.

Record before/after snapshots using compositor instrumentation; ordinary unprivileged Wayland apps cannot reliably enumerate other apps' windows. Keep the old shell running until the new one reports readiness; commit atomically from the user perspective. Test Firefox, terminal, editor, Qt app, and Xwayland clients. Test repeated changes, crash/restart of UI, failed shell launch, multiple outputs, suspend/resume, and real GPU variants later.

## 6. Proposed Cargo workspace layout

```text
Universal-Desktop-Manager/
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── AGENTS.md
├── PROJECT_STATE.md
├── README.md
├── LICENSE                    # Existing license must be preserved pending decision
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md         # If adopted
├── SECURITY.md
├── THIRD_PARTY_LICENSES.md    # As needed for distribution
├── Cargo.toml
├── Cargo.lock
├── crates/
│   ├── udm-app/
│   ├── udm-core/
│   ├── udm-ecs/
│   ├── udm-catalog/
│   ├── udm-compat/
│   ├── udm-packages/           # Later
│   ├── udm-package-helper/     # Later
│   ├── udm-sessions/           # Later
│   ├── udm-compositor/         # Later
│   ├── udm-bridge/             # Later
│   ├── udm-switcher/           # Later
│   ├── udm-shells/             # Later
│   └── udm-ui/                 # Later
├── desktops/
│   └── kde-plasma.toml
├── docs/
│   ├── architecture/
│   ├── design/
│   ├── development/
│   │   └── roadmap.md
│   └── adr/
├── packaging/
│   ├── systemd/               # Later
│   └── polkit/                # Later
└── tests/
    ├── integration/
    └── virtual-machines/      # Later
```

Initial setup creates only the structures and code meaningfully needed for v0.1, avoiding placeholder complexity.

## 7. Documentation division (agreed policy)

### GitHub Wiki = primarily **end-user manual**

User-friendly pages: Home, Getting Started, Installation, First Launch, Quick Start, Installing Desktops, Switching Desktops, X11 and Wayland (explained for users), Supported Desktops, KDE Plasma, Settings, Troubleshooting, Known Limitations, FAQ. Accurately label planned features as *not yet implemented*. No implementation internals are required in the wiki. It should be initialized if permissions permit; if unavailable, provide exact steps and starter pages for publishing.

### Main repository `docs/` = technical/developer documentation

- `docs/architecture/`: overview, Bevy ECS, compositor/Smithay, X11/Wayland, IPC, security boundaries.
- `docs/design/`: discovery, package management, sessions, switching, preservation contracts.
- `docs/development/`: building/testing, roadmap, release engineering.
- `docs/adr/`: architectural decision records, with statuses proposed/accepted/superseded/rejected.
- Rustdoc for public APIs. README is concise and points to wiki and developer docs.

The wiki must **not** be the sole technical specification or agent handoff store; technical changes should be reviewed in the same PR as code.

## 8. Durable plan tracking across agent sessions

**`AGENTS.md`:** Mandatory startup: inspect git branch/status, read `PROJECT_STATE.md`, relevant `docs/` and ADRs, inspect assigned issue/milestone, inspect code, plan scoped task. Mandatory closeout: run checks, report acceptance criteria, update issue/PR, update state when warranted, change relevant technical docs, hand off verified work, blockers and next step. Do not assume prior chat memory. Never claim success based merely on code written.

**`PROJECT_STATE.md`:** Compact handoff status: date verified, current milestone, last successful validation, implemented vs planned, blockers, issue/PR links, next action. Keep synchronized with verified repository state; not a diary or substitute for tests.

**GitHub Issues & Milestones:** Fine-grained approved tasks with description, dependencies, acceptance criteria, labels and milestone; PRs refer to issues. Suggested milestones v0.1, v0.2, v0.3, v0.4, v0.5, v0.6, v0.7–0.9, v1.0; group versions if GitHub limitations make ranges awkward. The live repository is authoritative for what issues actually exist.

**ADRs:** Record why Rust/Bevy, Smithay, runtime separation, preservation contract, wiki/docs boundary, distro backends were chosen. Distinguish decisions discussed from decisions accepted.

**GitHub Actions:** `cargo fmt --check`, Clippy, compilation, `cargo test`, with scoped security/license checks where practical. PR template asks which issue, what changed, tests, user-facing docs, technical docs, risks and handoff. CI cannot automatically prove semantic agent compliance.

**Source-of-truth map:** Technical roadmap → `docs/development/roadmap.md`; task progress → Issues and Milestones; current handoff → `PROJECT_STATE.md`; architecture → `docs/architecture` and accepted ADRs; agent rules → `AGENTS.md`; user manual → Wiki; actual behavior → code + tests.

## 9. Full product roadmap

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

## 10. Licensing decision still open — DO NOT CHANGE LICENSE WITHOUT APPROVAL

Prior conversation considered GPL-3.0-or-later and explained GPLv2 vs GPLv3. The reported current repository has a GPLv2 license file, **but the incoming agent must verify this live**. Keep existing `LICENSE` unchanged. Do not infer `GPL-2.0-only` versus `GPL-2.0-or-later` merely from a copy of generic GPLv2 text; obtain an explicit project-level choice and copyright notice before asserting SPDX metadata. Likewise, licensing the wiki under CC-BY-4.0 is only a suggestion until approved. Audit dependencies before distribution. Bevy and Smithay licensing compatibility should be verified at pinned versions.

## 11. Safety and non-goals

- No root-level package installation or compositor takeover during v0.1.
- Never quietly restart GDM/SDDM or the active graphical session during installation.
- Do not install from arbitrary internet scripts or inject unknown repositories.
- No claims of universal X11↔Wayland migration.
- No assumptions that installed native KDE components can run inside a custom shell.
- Never make the management UI's lifecycle an implicit kill switch for applications.
- No application or package change without an approved scope and tested fallback.
- Early compositor/native-session experiments belong in nested sessions or disposable VMs, not as a developer's primary desktop.

## 12. EXACT initial repository-setup task for the incoming Work session

**Primary assignment: set up repository infrastructure and v0.1 foundations; do not attempt the entire product roadmap.**

### A. Reconnaissance

1. Inspect `https://github.com/WhatzGames/Universal-Desktop-Manager`, `main`, files, license, existing workflows, wiki, issues, and milestones using authenticated GitHub tooling when connected. If unavailable, explicitly report limitations rather than inventing status.
2. Identify repo protections and permissions. Work on a separate `setup/v0.1-foundation` branch (or another appropriate nonconflicting branch); do not overwrite unrelated work.
3. Confirm available stable Rust/Bevy versions and compatible dependency versions using upstream documentation. Pin dependencies appropriately.

### B. Implement functional v0.1 project skeleton

1. Create workspace root manifest, lockfile, `udm-app`, `udm-core`, `udm-ecs`, `udm-catalog`, `udm-compat` (or a smaller justified organization if it avoids empty crates).
2. Add a minimal executable Bevy ECS app that loads desktop catalog/state, detects host basics read-only, and prints or displays a truthful compatibility summary.
3. Include ECS unit tests and maintain clear boundaries between discovery/compatibility and future side-effecting modules.
4. Add `README.md` with project overview, honest feature status, build/test instructions and links to wiki and `docs/`.
5. Preserve `.gitignore` and existing `LICENSE`; do not invent license metadata.

### C. Persistent governance files

1. Create `AGENTS.md` with mandatory read/implement/test/document/handoff rules described in Section 8.
2. Create `PROJECT_STATE.md` clearly identifying verified current status, completed implementation, blocker links, current milestone and next action.
3. Add `docs/development/roadmap.md` containing the full phase-by-phase plan from this file, not an abbreviated or materially different version.
4. Create initial architecture docs, design docs and ADRs; label proposals appropriately. This file may be preserved in the repo as `docs/development/master-plan.md` verbatim or copied with only harmless formatting edits so **the exact plan is not lost**.

### D. GitHub management

1. Create milestone(s) starting with v0.1 and plan through v1.0, without claiming releases exist.
2. Create actionable v0.1 Issues: workspace foundation, Bevy ECS, catalog, distro detection, session discovery, KDE compatibility, CI, documentation. Mark tasks already done by the setup PR as appropriately covered, avoiding duplicate issues.
3. Add issue templates, pull-request template, and GitHub Actions CI (`fmt`, `clippy`, `build`, `test`), then run checks.
4. Enable/initialize the Wiki if authorized/permitted. Wiki pages should be user-centric and mark unreleased functionality as planned. If GitHub tooling cannot initialize wiki, create ready-to-publish content and provide exact manual instructions.

### E. Deliverables and completion

1. Open a pull request from the setup branch to `main`, **do not merge**.
2. Share PR URL, changed files, build/test results, created issues/milestones, wiki status, current blockers and next task.
3. Update `PROJECT_STATE.md` and relevant issues with objectively verified results before completing the session.
4. Do not claim completion of v0.1 features that are still stubs or not tested.

### Initial setup acceptance checklist

- [ ] Repository state and license inspected live and preserved.
- [ ] Cargo workspace builds from a clean checkout.
- [ ] Bevy ECS application runs without privileged side effects.
- [ ] Desktop discovery and KDE compatibility results are truthful and tested (or clearly reported incomplete).
- [ ] `AGENTS.md`, `PROJECT_STATE.md`, and complete roadmap/master plan committed.
- [ ] Technical documentation is in `docs/`; user guidance is in GitHub Wiki or publish-ready Wiki files.
- [ ] CI runs formatting, lint, build and tests.
- [ ] Issues, milestones and handoff recorded if access permits.
- [ ] Pull request opened without merging.

## 13. Standard future-agent session checklist

At start: `git status` → read `AGENTS.md` → read `PROJECT_STATE.md` → read `docs/development/master-plan.md` and relevant ADR/design docs → inspect assigned issue and branch → inspect code and baseline tests → scope work.

At end: validate code and expected behavior → update docs/issues/ADRs as relevant → update project state only with evidence → push branch/create or update PR → summarize what changed, what is unverified, blockers, and next task.

**Never rely on cross-session conversational memory as the authoritative plan. The Git repository, issues, test results, and recorded decisions are the enduring record.**
