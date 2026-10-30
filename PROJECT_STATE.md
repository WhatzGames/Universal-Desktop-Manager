# Current project state

Rust language requirement confirmed 2026-10-30: all shipped UDM-owned runtime code,
including the privileged package helper, must be Rust. The Python backend was an
implementation shortcut and still requires migration; it is not an approved target
architecture. ADR 0002 now distinguishes legacy behavior/evidence from the required
Rust replacement. Rust APT bindings exist but coverage has not been validated or a
dependency selected. Python CI/test tooling is separate. No runtime migration or
new native installation was performed in this documentation correction.
The user explicitly permits FFI: external libraries may retain their native code,
but all UDM-owned application logic stays Rust; bridge code is limited to type/call
adaptation. Preserve authorization, validation, journal/recovery and no-shell policy.

Runtime integration requirement clarified 2026-10-30: library/API-first system
operations, no shell-command evaluation. Installer resolution/commit already use
python3-apt; apt-cache availability, dpkg audit and fixed helper/pkexec launches
remain documented process-based gaps. [Inventory and contract](docs/design/process-execution.md).
This is a persistent requirement/documentation update, not a completed runtime
migration or a guarantee against every RCE. No installation was authorized or run.

Verified 2026-10-30. The snapshot-based Debian 13 CI objective is implemented and
validated in a disposable GitHub-hosted KVM guest. This is not a release claim.

## Review and preservation

- Merged PR #12/main 2ae133afc1af808b6a6d4d0354d206a16cb842b0 is incorporated.
- Draft PR #13 remains unchanged at security fix 67165a29fea157ea48926b3a5a96e68e1c510057.
- Draft [PR #14](https://github.com/WhatzGames/Universal-Desktop-Manager/pull/14)
  stacks on PR #13, retaining the faster real Plasma container check. No PR merged
  or history rewritten. Original setup/PR #13 worktrees are preserved.
- Integration branch ci/debian13-snapshot-vm; approved execution branch
  ci/debian13-install-approved. Personal SSH signing/attribution remain enabled.
- LICENSE/SPDX, Rust 1.99.1, restricted helper and deployed Polkit policy unchanged.
- WhatzGames is active in gh with repository ADMIN access. No tokens enter guests.

## Authoritative accepted evidence

[Complete result and limits](docs/development/validation/v0.2-vm/kvm-fixed/accepted/README.md).
[Passing run 40975763374](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40975763374).

- Executed source: 4d3c188b9a94166e1e50a4b7fbb34bfb6a830697.
- Preparation: 40975306873, 117.100 seconds, running RAM/disk restore verified.
- Manifest: 15eaf3fcb54f542beda9b57a9dc3b6c20d13cebe78cbf65d1c7d34fee55a9edc.
- Transaction: ed20b81bb265c6549f47ecd5b978ac1affe0b79e694ed25da8f1e62381266fa9.
- Signed owner approval-only commit: a508ea6fb41f7895b316687f10e6f33caca352bd.
- KVM, fixed Westmere-v1,phys-bits=40,enforce; reviewed QEMU/files/source revalidated.
- Human approved exact KVM scope and reaffirmed continuation after observer fixes;
  the complete transaction including repository fingerprints remained identical.

Real Rust CLI → pkexec → restricted helper added exactly 579 reviewed packages;
zero removals or changed existing versions, ready journal for authenticated UID 1000,
clean dpkg audit, executable launcher and Wayland session definition. No activation.
Original XFCE/LightDM PID/start/session identities remained identical in every case.

Stale plan, native download failure, native dpkg pre-invoke failure, actual dpkg
--unpack interruption with installing journal and blocked retry, and native commit
followed by helper verification failure all passed. Separate UID 1001 ran real KWin
Wayland/QPainter and Plasma with one desktop/panel and a rendered wallpaper. Final
snapshot recovery reproduced original full transaction, inventory and desktop identities.

## Trigger and review boundaries

Ordinary pushes run fast CI only. Preparation requires integration branch plus
[vm-prepare] title marker; TCG needs its separate [vm-prepare-tcg] marker. Installation
requires an existing dedicated branch, exactly one non-forced signed/Verified owner
commit changing only approval JSON, exact manifest title and explicit source/run/
manifest/transaction/mode approval. Small provenance artifacts are checked before
VM scheduling. Semantic repeats, reruns and unrelated/mixed-file pushes fail closed.
[Protocol](.ci/README.md), [real rejection/non-trigger tests](docs/development/validation/v0.2-vm/push-gate/README.md).
A true record is now on the approval branch; it does not authorize ordinary pushes
or additional transactions. No local/host package installation or native repair.

## Calibration and known limits

Original host-passthrough KVM snapshot failed Intel-to-AMD restoration and is withdrawn;
[failed evidence](docs/development/validation/v0.2-vm/kvm-portability-failure/README.md).
Fixed-model preparation 40971706077 and independent restore 40972477946 passed.
First acceptance 40973063920 caught read-only dpkg during planning; second 40974425288
missed native dpkg across process groups and installed successfully. Their evidence
is preserved; the final observer follows exact ancestry and mutation arguments.
TCG preparation/local read-only replay remains historical fallback calibration.

Interactive administrator password prompts, partially configured maintainer-script
recovery, native repair, full guest power loss, physical GPU/input, native activation
and window migration are untested/out of scope. The dpkg hook fails before unpacking;
interruption proves a native command/journal interruption, not all script states.
Maintainer scripts are privileged; policy-rc.d is not a sandbox. Snapshot restoration
is the reviewed recovery, not APT rollback. Guest reports spec_store_bypass Vulnerable;
public-data disposable VM only, no production security claim. Runner compatibility
is measured, not universal; unsupported CPU/QEMU/acceleration fails closed.

14 VM tests, 16 helper tests, Cargo fmt/Clippy/locked build/test (7 Rust tests),
read-only reports, Debian simulation and retained Plasma PR CI pass on executed source.
Source/snapshot artifacts have seven-day CI retention; expiry/change needs a fresh
review. Native acceptance captures, summaries, log hashes and screenshots are published.
Issues #10/#11 and milestone v0.2 remain open for review; PR #13/#14 remain draft and
unmerged. No release was published. Offline CachyOS miix320 was not used or connected.

All six affected Wiki pages are published in signed commit
61111025c31a4c9a77300f0c889d649ad3207299 after specific human approval; every
page matches the integration source bytes. PR #14, issues #10/#11 and the open
v0.2 milestone now link the passing native evidence and preserve remaining limits.

## Tooling image refresh and newest-image CI — current change

The image action pulls current Debian 13, upgrades packages without build-cache reuse,
exports image/inventory/checksums, reloads the archive and smoke-tests tools. Push
build 41105262099 and manual refresh 41105512320 both passed. VM CI now resolves the
newest successful producer at job startup, validates source/recipe/archive/image
identity and binds it into the review manifest. Image drift after review fails
closed and requires fresh preparation/approval. Old accepted evidence above is
historical and unchanged; this update authorizes no further installation.
19 VM unit tests pass, including provenance, recipe/architecture/hash mismatches,
old reviews and latest-image drift. Fresh read-only preparation 41105790965 passed in 88.759 seconds, selected manual
refresh 41105512320 and restored identical original baseline/transaction/inventory.
The hard-coded historical KVM restore workflow was retired; its evidence is retained.
Details and artifact usage: tests/vm/TOOLING.md.

[Tooling artifact evidence](docs/development/validation/v0.2-vm/tooling-image/README.md)
retains both build identities and the consumer review manifest. Approval controller
de46e73 uses the same latest-image policy; its approval file remained byte-identical
and no installation workflow was triggered. PR checks passed on 7b27076. This
tooling transport/update change has not rerun native installation; that remains
historical accepted evidence on 4d3c188, with new review required for this snapshot.
