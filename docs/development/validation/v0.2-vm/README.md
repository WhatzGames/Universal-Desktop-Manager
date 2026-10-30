# Debian 13 running-snapshot review — 2026-10-29

**Current result: [approved KVM acceptance passed](kvm-fixed/accepted/README.md): real installation, documented failures, original desktop continuity, isolated Plasma and final snapshot recovery.**

The remainder of this page retains historical evidence. Its old source/digests are not the accepted KVM identities.

The original KVM candidate below is **withdrawn** for cross-runner use after a real
Intel-to-AMD restore failure. [Evidence and replacement work](kvm-portability-failure/README.md).
Its same-runner success does not prove portability. TCG evidence remains valid.
Draft [PR #14](https://github.com/WhatzGames/Universal-Desktop-Manager/pull/14) stacks
on draft PR #13 at 67165a2, preserving the mixed-origin fix and merging main 2ae133a
from merged PR #12. Neither #13 nor #14 was merged.

Tested source: `fc9df23f06b5b79c06a7259bc9f0358ae388acc8`, confirmed GitHub Verified.
Frozen review ref: `ci/debian13-vm-review-fc9df23`. Later handoff/evidence-only commits
on the integration branch do not change the source approved for these snapshots.
The complete [protocol](../../../../tests/vm/README.md) documents the gate and cases.

## Measured preparation

| Execution | Result | Preparation seconds | Evidence run |
|---|---|---:|---|
| Hosted Ubuntu 24.04, actual KVM initialization probe | Passed | 154.614 | [40952610168](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40952610168) |
| Hosted Ubuntu 24.04, forced QEMU TCG | Passed | 426.476 | [40952610041](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40952610041) |
| Local macOS ARM64 → Podman ARM64 QEMU TCG (earlier c26d598) | Desktop/plan/denial/snapshot created | 450.467 | `target/vm-review-c26d598/`; predates automated restore proof, not an approval candidate |

Times cover image download/check, guest provisioning, native plan, denial, snapshot
save and (for hosted runs) restored baseline checks; tooling builds and artifact
upload are outside the measured preparation timer. Both hosted runs used QEMU
10.0.13, Debian package `1:10.0.13+ds-0+deb13u1`.
Software emulation is feasible for this measured preparation. A dedicated runner
was not required for these runs. Full installation/failure-suite duration is still
unmeasured; do not infer that it fits the 120-minute job limit. GitHub
[does not officially support nested virtualization](https://docs.github.com/en/actions/concepts/runners/github-hosted-runners).
Observed KVM availability is not a guarantee for later runners.

Both guests started a real XFCE desktop through LightDM with systemd/logind and
Polkit. The captures retain boot/machine/VM UUID, PID and /proc start identities for
xfce4-session, xfwm4, xfdesktop and xfce4-panel, active local X11 session, LightDM
PID/start identity and configuration, and a screenshot. Preparation restored the
RAM/disk snapshot and asserted identical baseline, full transaction and package
inventory. Default Polkit denied the real CLI/pkexec request; inventory was unchanged
and no operation JSON was created. This is denial evidence, not interactive password
prompt or successful installer authorization evidence.

The cloud image's official mirror+file repositories expose empty origin sites.
The strict helper correctly refused those origins. Guest provisioning saves the
original definitions and narrows sources to explicit official Debian HTTPS
trixie/updates/security before refreshing metadata. The helper policy is unchanged;
no backports or unknown repository is added. Source definitions are in both baseline
summaries. The source/SHA512 image identity is in the review manifests.

## Exact transaction to review

[Complete transaction](transaction.json) and [original package inventory](packages-before.txt).
Both hosted guests produced the same complete transaction and inventory:

- 579 NEW packages; all seven KDE/Wayland target packages are proposed.
- No removal, upgrade, reinstall or new display-manager package.
- All candidate origins are trusted Debian at deb.debian.org/security.debian.org.
- Download estimate: **275,013,144 bytes**.
- Additional installed-size estimate: **989,224,960 bytes**.
- UDM SHA256: `f958050ea5fdaf430c5ecec486d6b14529d02e9c6791e0c2850973071b8a6e3f`.

These are metadata estimates, not reserved disk space or an installation-safety
claim. Transaction equality does not make the two VM snapshots interchangeable.
Approval must name one exact manifest and its snapshot/source identity.

| Identity | KVM | TCG |
|---|---|---|
| Review manifest | [kvm-review.json](kvm-review.json) | [tcg-review.json](tcg-review.json) |
| Manifest SHA256 | `24888a508b6575c42e8de9d9bfae490d5e0bce3f6b7161f8255b975ed6bcc621` | `095cbefa5861fb779d72a8e433fe8cb27e73adf0c4d5b4c8d633b3ab772345df` |
| Disk SHA256 | `92f13de8e58a2c4308b5df0fbce1fddbb8c205025bffe401684dfd785ad59084` | `a44546bc66aa2d4f9e5936c9364ac6207a58a8c8c4b43aa41b7ecdabd6041f33` |
| Snapshot artifact ID | 12932671232 | 12932895794 |
| Compressed artifact bytes | 1,293,914,284 | 1,294,005,329 |
| Original desktop after restore | [KVM screenshot](kvm-restored-desktop.png) | [TCG screenshot](tcg-restored-desktop.png) |
| Restore/inventory checks | [KVM checks](kvm-checks.json) | [TCG checks](tcg-checks.json) |
| Default Polkit denial | [KVM](kvm-denial.json) | [TCG](tcg-denial.json) |

`*-baseline-summary.json`, `*-snapshots.txt`, `*-execution.json` and `*-serial.log`
retain original desktop/source identity, memory snapshot list, acceleration probe
and complete guest provisioning text logs (ANSI/carriage returns and trailing
whitespace normalized; original raw serial logs remain in CI/local evidence). The unmodified full baseline/restore JSON and
raw command stdout/stderr are retained in each CI evidence artifact and local
`target/hosted-fc9df23-{kvm,tcg}-evidence/`. The summaries avoid duplicating the identical
579-package transaction; checks record hashes of the original full JSON.

The separate `debian13-reviewed-snapshot` artifacts retain the disk, source/seed ISOs,
UUID, full baseline and manifest. They contain no supplied credentials or GitHub token;
guest passwords are locked, SSH keys are not generated and SSH is disabled. CI retention
is seven days; expiry requires a fresh snapshot/review if no intact local copy remains.
Never substitute another disk or weaken digest/source/QEMU validation.

## Approval still required

A human must review the complete transaction and approve **one exact manifest** before
running acceptance. Approval includes only this disposable guest's real install,
intentional stale/download/dpkg/interruption/verification-failure cases, and reviewed
snapshot restoration between them. It does not authorize a primary desktop, package
repair, unknown repositories, logout, display-manager restart, native activation,
physical GPU/input claims or window migration. The harness's temporary Polkit test
rule is restricted to the exact helper command/digest and desktop user; deployed
Polkit policy remains unchanged. Maintainer scripts run privileged; policy-rc.d is
not a sandbox. The original desktop must survive actual installation assertions.

After explicit approval of the **TCG** manifest above, an authorized Actions operator
can dispatch the exact reviewed source (this command is a reviewable proposal, not
an instruction or implicit permission to execute it now):

```sh
gh workflow run ci.yml --repo WhatzGames/Universal-Desktop-Manager \
  --ref ci/debian13-vm-review-fc9df23 \
  -f stage=accept -f review_run=40952610041 \
  -f review_sha256=095cbefa5861fb779d72a8e433fe8cb27e73adf0c4d5b4c8d633b3ab772345df \
  -f plan_digest=f958050ea5fdaf430c5ecec486d6b14529d02e9c6791e0c2850973071b8a6e3f \
  -f runner=ubuntu-24.04 -F software_only=true
```

The earlier CLI account could not dispatch workflows (403). WhatzGames is now the active account with repository ADMIN access; the selected route remains the strictly gated push. Both full hosted snapshots are also retained locally under
`target/hosted-fc9df23-{kvm,tcg}-snapshot/`. All KVM files were hash-validated; the
TCG files were hash-validated on an APFS clone before replay. The original copies
remain intact.

A local restore-only calibration also **passed in 69.626 seconds** using amd64
container-scoped QEMU on the Mac's existing ARM64 Podman appliance (emulated amd64
userland). The QEMU binary SHA256 exactly matches the hosted snapshot, and the
reported amd64 architecture/TCG mode, full guest baseline, transaction and inventory
match. [Calibration result](local-tcg-restore.json) · [Restored desktop](local-tcg-restored-desktop.png).
Only read-only capture/plan was invoked; no installation authorization or install
command ran. This provides a calibrated local execution route after the same exact
human transaction approval, without expanding GitHub credentials. Use the immutable
original TCG snapshot and the packet's exact source/digests, not the mutated calibration
copy. Full installation-suite performance and results remain unverified. The approval gate is never replaced by generic workflow access.

## Validation and remaining acceptance

macOS formatting, warning-free Clippy, locked build/tests (7 Rust tests), read-only
report and 16 helper tests passed; 5 VM-focused tests pass. Linux Cargo/helper/VM
checks and the retained real Plasma container PR job passed on fc9df23:
[PR CI 40952617549](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40952617549).
Official Rust stable was fetched on 2026-10-29 and remains 1.99.1; pins and LICENSE/SPDX
terms are unchanged. The mixed Debian/local-origin rejection is preserved.

**NOT RUN:** approved KDE commit; positive Polkit authorization; native download/dpkg
failure and interruption; durable native operation/recovery assertions; helper
post-commit verification failure; original desktop preservation during install;
and guest KWin/plasmashell readiness. The original PR #12 container result does not
satisfy those assertions. Interactive auth_admin prompt, partially configured
maintainer-script failure, native package repair, full guest power loss and physical
GPU/input remain separate limitations. Issues #10/#11 and milestone v0.2 stay open.
No host package was installed, the PR #13/setup worktrees were preserved, and offline CachyOS
miix320 was not used or given internet access.

## GitHub-only push route

The [dedicated signed push gate](../../../../.ci/README.md) avoids workflow-dispatch
credential changes and local execution. Publishing the gate is not approval. The
example is false, and no true record is included on the integration branch. The
approval commit must name this exact manifest/source/run/transaction and pass all
branch, path, signing, owner, single-commit and repeat/rerun checks. It checks out
the frozen guest source rather than treating the approval commit as a new snapshot.
