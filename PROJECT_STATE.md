# Current project state

Verified: 2026-10-29. Active persistent goal: snapshot-based Debian 13 VM CI for
v0.2. **Preparation is validated; real KDE installation acceptance is not complete.**

## Branches and review

- Foundation PR #1 is merged; issues #2–#9 are closed.
- PR #12 is merged as main `2ae133afc1af808b6a6d4d0354d206a16cb842b0`.
- Draft [PR #13](https://github.com/WhatzGames/Universal-Desktop-Manager/pull/13)
  remains at `67165a29fea157ea48926b3a5a96e68e1c510057`, including mixed-origin rejection.
  Its branch/worktree and the original setup worktree were preserved.
- Draft [PR #14](https://github.com/WhatzGames/Universal-Desktop-Manager/pull/14)
  is stacked on PR #13's branch. Integration worktree:
  `/Users/obedkooijman/CodexProjects/worktrees/Universal-Desktop-Manager-snapshot-vm`,
  branch `ci/debian13-snapshot-vm`. It merges main without rewriting PR #13.
- Validated executable CI source: `fc9df23f06b5b79c06a7259bc9f0358ae388acc8`,
  confirmed GitHub Verified. Frozen review ref: `ci/debian13-vm-review-fc9df23`.
  Later evidence/handoff-only commits do not change the source of the reviewed VMs.

Do not merge #13/#14, publish a release, close #10/#11 or complete milestone v0.2
without actual acceptance evidence. LICENSE/SPDX terms and Rust 1.99.1 pins are unchanged.

## Implemented candidate

Read-only default report plus explicit package CLI and root-owned isolated-Python
helper using Debian python3-apt. Fixed KDE targets, complete review JSON, SHA256-bound
locked re-resolution, trusted origins, Polkit, no arbitrary UI commands/repositories,
no removals/upgrades/reinstalls/new display managers, durable atomic/fsynced operation
records and manual native recovery guidance. Verify target packages, dpkg audit,
launcher and Debian's wrapped Wayland session. No session activation/live switching.
See installation design, ADR 0002 and packaging/debian/README.md.

`tests/vm/` now provisions a real disposable Debian 13 XFCE/LightDM guest with
systemd/logind/Polkit, QGA/QMP control and a RAM/disk snapshot. Preparation records
original process/session/display-manager identity, full exact transaction and source/
snapshot hashes, tests default Polkit denial, then restores and compares baseline,
inventory and complete transaction. Guest passwords are locked, no SSH keys are
generated and no GitHub credentials enter the guest. The cloud image's mirror+file
sources correctly fail strict origin validation; provisioning retains their original
definitions and uses explicit official Debian HTTPS sources before planning.

The two-stage manual workflow requires exact source, preparation run, manifest and
plan digests before install, validates downloaded snapshot/QEMU identity and guest
state, then uses the actual Rust CLI → pkexec → installed helper. A temporary test
Polkit rule is limited to the exact helper command/digest and desktop user. It does
not validate the deployed policy's interactive administrator password prompt.
Each destructive case restores the reviewed snapshot. Native failure/success and
isolated real KWin/plasmashell tests are implemented but NOT RUN until approval.
The faster PR #12 container component smoke job is retained.

## Verified evidence

[Complete review packet, exact 579-package transaction, identities, screenshots and
limitations](docs/development/validation/v0.2-vm/README.md).

- Hosted KVM preparation and RAM/disk restore passed in **154.614 seconds**:
  https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40952610168
- Separate hosted TCG preparation and restore passed in **426.476 seconds**:
  https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40952610041
- Both produce identical transaction/inventory; all seven KDE targets proposed,
  579 new packages, 275,013,144 download bytes, 989,224,960 additional installed bytes
  estimated, no removals/upgrades/new display managers, trusted official Debian origins.
- Full transaction digest:
  `f958050ea5fdaf430c5ecec486d6b14529d02e9c6791e0c2850973071b8a6e3f`.
- TCG review manifest SHA256:
  `095cbefa5861fb779d72a8e433fe8cb27e73adf0c4d5b4c8d633b3ab772345df`.
  KVM manifest SHA256:
  `24888a508b6575c42e8de9d9bfae490d5e0bce3f6b7161f8255b975ed6bcc621`.
  Approval must select one exact snapshot, not just the shared transaction digest.
- Default Polkit denied CLI/pkexec installation, no operation JSON was created,
  inventory and original baseline were unchanged. Original XFCE screenshots inspected.
- Local earlier c26d598 ARM64 QEMU TCG guest prepared a desktop/plan/denial/snapshot
  in 450.467 seconds; that older run is not the final approval candidate.
- macOS fmt, warning-free Clippy, locked build/test (7 Rust tests), read-only report,
  16 helper tests; 5 VM-focused regression/boundary tests pass. Official Rust stable
  manifest fetched 2026-10-29 still reports 1.99.1.
- Linux Cargo/helper/VM tests and retained real Plasma container PR CI pass on fc9df23:
  https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40952617549

Full source/snapshot artifacts retain the reviewed guest for seven days in CI;
local evidence is under `target/hosted-fc9df23-{kvm,tcg}-evidence/`. Complete immutable snapshot
copies are retained under `target/hosted-fc9df23-{kvm,tcg}-snapshot/`; all KVM files
were hash-validated and all TCG files validated on a clone before local replay.
Never substitute another guest or weaken QEMU/source/digest checks. No KDE was installed.
TCG is feasible for measured preparation; full suite runtime is still unmeasured.
No dedicated runner was needed for these runs, but hosted nested virtualization is
not officially supported and later KVM availability is not guaranteed.

## Approval boundary and remaining acceptance

**No exact VM transaction is approved yet.** Review the full packet and obtain
explicit human approval before any real KDE commit or destructive case. Implemented
acceptance cases: stale digest, isolated-network download failure, native dpkg hook
failure, observed-dpkg process interruption with blocked retry, native commit followed
by helper verification failure, success plus isolated software-rendered Plasma, and
reviewed final snapshot recovery. Native package repair is never automated.

Actual approved installation, positive Polkit authorization, native failure/journal/
recovery assertions, original desktop survival through installation and guest Plasma
readiness remain UNVERIFIED. Maintainer scripts are privileged; policy-rc.d is not a
sandbox. Interactive auth_admin prompt, partially configured maintainer-script failure,
full guest power loss, physical GPU/input and general native window migration are
separate limitations. No v0.3 activation, logout or display-manager restart is invoked.

The CLI credential lacks workflow-dispatch permission (403), and the new standalone
workflow is not registered on main. The registered ci.yml calls the reusable workflow;
scoped integration pushes prepare only. After exact approval an authorized Actions
operator can dispatch ci.yml at the frozen review ref using the packet's exact inputs.
The exact hosted TCG snapshot also passed a local restore-only calibration in
69.626 seconds using matching amd64 QEMU tooling on the existing ARM64 Podman appliance
(emulated amd64 userland). Baseline, complete plan and inventory match; no install
command or authorization ran. This calibrated local route can run the real suite
only after explicit approval of the TCG manifest and transaction. Use the immutable
original snapshot, not the calibration copy; no account permission expansion is needed. Generic workflow access is not installation
approval. Keep #11 and milestone v0.2 open.

miix320 is offline LAN-only CachyOS. It was not used as a Debian VM and its internet
was not enabled. No host package was installed.

## Documentation and tracking

Issues [#10](https://github.com/WhatzGames/Universal-Desktop-Manager/issues/10) and
[#11](https://github.com/WhatzGames/Universal-Desktop-Manager/issues/11), milestone
[v0.2](https://github.com/WhatzGames/Universal-Desktop-Manager/milestone/2), and draft
PR #14 track this candidate. Technical protocol: tests/vm/README.md. Historical
container-only simulation evidence remains in docs/development/validation/v0.2/.
Wiki source pages and published manual distinguish preparation from installation;
signed a13db2c publishes the verified preparation/restore status while keeping
installation unapproved. Personal SSH signing and
My Flow attribution hooks are retained. No permission scope was broadened.

## Narrow push approval path (validated denial/filtering)

The user selected GitHub-only push execution with strict overtrigger protection.
`.ci/README.md` specifies the dedicated existing branch + single approval-file
change + one non-forced signed owner commit + exact manifest commit title. JSON
must explicitly approve exact source/run/manifest/transaction/mode; small review
artifacts are validated before scheduling the expensive VM. Semantic repeats and
workflow reruns cannot install. No true approval record is published by the
integration branch. Choosing this mechanism is not approval of the 579-package plan.
The reusable workflow executes the reviewed source independently of the newer
approval commit; prior fc9df23 snapshots remain the candidate. Ordinary integration
pushes no longer provision VMs: `[vm-prepare] ` is required for push preparation.
Native acceptance remains unapproved and not run.

Gate source 6b4559a is GitHub Verified; integration CI 40965589506 passes with
heavy VM work skipped for an ordinary push. Dedicated branch/worktree
`ci/debian13-install-approved` / `Universal-Desktop-Manager-install-approved` is
bootstrapped. Its false-record test 40965706342 is an EXPECTED denial: approval
fails specifically for approved:false and acceptance is skipped. A subsequent
documentation-only push (40965924225) creates only normal CI, no approval workflow.
[Gate evidence](docs/development/validation/v0.2-vm/push-gate/README.md).
All required Cargo checks/report, 7 Rust tests, 16 helper tests and 10 VM-focused
tests pass. The actual watched record remains false; no true approval is published.
The user selected GitHub-only execution. An eventual signed true approval push
uses the existing SSH transport and frozen guest source, so CLI dispatch permission
and local VM execution are no longer needed for acceptance. Real install remains
unapproved and unverified; #11 and v0.2 remain open.

## KVM proposal correction — independent runner failure

Read-only KVM cross-runner test 40969898313 rejected the original host-bound saved
register state: initial guest Intel Xeon 8573C, new runner AMD EPYC 7763. No guest
capture, authorization or installation ran. Old KVM manifest 24888a... is withdrawn
for hosted push acceptance, and the gate rejects it. Same-host restore evidence did
not prove cross-host portability. [Failure evidence](docs/development/validation/v0.2-vm/kvm-portability-failure/README.md).
Replacement KVM preparation uses a fixed versioned Westmere-v2 model, fixed 40-bit
physical width and enforced feature support, recording/checking the model in the
manifest. A fresh candidate and independent restore are required before approval.
TCG remains fallback-only; its separate experiment now requires [vm-prepare-tcg].
No exact package transaction is approved; no true approval record exists.
