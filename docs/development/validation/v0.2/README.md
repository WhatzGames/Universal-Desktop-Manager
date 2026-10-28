# v0.2 validation evidence — 2026-10-28

Base: merged v0.1 PR #1, main `3bca2623e3cabf15bc8341f2d060aa482aceed15`.
Branch: feature/v0.2-debian-kde. These results do not satisfy installation acceptance.

## Observed

- Official Rust stable channel manifest dated 2026-10-15 identifies Rust 1.99.1;
  local rustc is 1.99.1. Toolchain/manifest/CI pins remain consistent.
- macOS aarch64: Cargo formatting, warning-free Clippy, locked build and seven Rust
  tests passed; default report remains read-only (macos-report.json).
- Sixteen Python safety tests passed without APT or root host modifications:
  forbidden transactions/origins, digest/authorization, changed-plan refusal,
  failure and verification phases, interrupted-operation refusal, atomic journal,
  existing service-policy preservation and exception cleanup, Debian wrapped launcher.
- A disposable Debian 13 ARM64 container on the existing Podman VM provisioned only
  python3-apt test dependencies. KDE was NOT installed. Image identity is recorded
  in debian-image-digest.txt. Native resolver ran twice as UID 65534 with identical
  JSON/digest results. packages-before/after.txt are equal; SHA-256:
  f9d043693fcdc1f84100b3a78f5c60ac02a95adc38845883b0441005f5b34de8.
- Simulation: 798 NEW packages, 364,910,796 download bytes, 1,455,311,872 installed
  bytes estimated; zero removals/upgrades/display-manager additions. Complete versions,
  origins, dependencies/conflicts and state fingerprints: debian-plan.json.
  Review digest: 91021a21da731ffe1a0aa136ae5e246e0c158ffa9f0da179936e6a8e5ad6bd51.
- Pre-install verification truthfully reports missing target packages, no executable
  launcher or session entry, clean dpkg audit, ready=false and no session started.
- Container removed after the checks. The test script repeats this read-only procedure;
  CI has a separate Debian 13 simulation job. Local evidence is ARM64, not x86_64.

The plan belongs to the deleted test container. It is reviewable simulation evidence,
not an authorization or reusable installation transaction for a different machine.
Regenerate and review a plan in the actual snapshot VM before requesting installation.

## Source-origin regression

A mixed candidate with both an allowed Debian origin and a local file-repository
origin reproduced a validation bypass: empty-site origins were discarded. The
regression failed before the fix. All candidate origins are now checked, so an
empty/unknown local site cannot hide behind an allowed Debian source. The synthetic
fixture covers this boundary; native source selection for a hostile repository has
not been exercised in a VM. Existing official-only simulation evidence is unchanged.

## CI

Push and PR CI passed on bba56f1, including the Debian x86_64 native simulation job:
- https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40780259048
- https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40780213650

CI evidence artifacts retain the x86_64 plan and package inventories for seven days.
Neither job installs KDE or validates an active desktop.

## Remaining acceptance blocker

No disposable Debian 13 desktop VM with snapshots is configured. Podman's appliance
and Debian container do not provide that environment. No actual KDE installation,
Polkit authentication, maintainer-script behavior, original-session/display-manager
continuity, crash/power-loss or real dpkg recovery has been validated. Fake failure
injection tests establish application state handling only. No graphics readiness or
session activation claim follows. Do not use this candidate on a primary desktop.

Next: provision a disposable Debian 13 desktop VM, record snapshot identity and running
session/display manager, install the reviewed helper prerequisites, generate the VM's
plan, present the exact package transaction and request explicit installation approval.
Then test success plus denied authorization, stale review, download failure, dpkg failure,
interruption and verification failure, restoring snapshots between destructive cases.
Never use offline CachyOS miix320 as the Debian installation VM.
