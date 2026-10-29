# Debian 13 snapshot VM acceptance candidate

This harness is under validation. A written workflow is not installation acceptance.
It supplements the fast, isolated Plasma container smoke job from merged PR #12 and
uses the restricted helper from draft PR #13, including origin fix 67165a2. The
integration branch merges main without rewriting PR #13. PR #13 and this integration PR remain unmerged.

## Review and approval

Run the existing `ci.yml` dispatch entry with `stage=prepare` at the reviewed
integration revision (it calls `debian-vm.yml`). During development, pushes to the
exact `ci/debian13-snapshot-vm` branch also run preparation only; they cannot approve
or enter acceptance. The new workflow is not yet registered on main, and the CLI
credential cannot dispatch workflows. The scoped push entry enables hosted
preparation without changing main or granting permissions. Preparation builds the Rust CLI and container-scoped QEMU tooling, downloads
the official Debian generic amd64 image over HTTPS, checks Debian's published SHA512,
and records the image checksum and URL. The checksum is retrieved over Debian HTTPS;
there is no independent image-signature verification in this candidate. APT uses
Debian's signed indexes and trusted package origins. The cloud image's mirror+file
source definitions yield empty origin sites and are correctly rejected by the helper.
Provisioning saves those definitions, then narrows the disposable guest to explicit
official Debian HTTPS trixie/updates/security sources before refreshing indexes. No
backports or unknown repository is added; the helper's origin policy is unchanged. No host packages are installed.

Cloud-init provisions only the original XFCE desktop, LightDM, systemd/logind,
Polkit, python3-apt, guest agent and test dependencies. There are no guest passwords,
SSH access keys, GitHub tokens or exposed guest network services. SSH is stopped and
host keys removed. QGA/QMP sockets exist only in the tooling container/state directory.
Do not upload arbitrary pre-existing disks or provision personal credentials.

Preparation requires live xfce4-session/xfwm4/xfdesktop/xfce4-panel processes, active
local X11 logind session, active LightDM, clean dpkg audit and a rendered screenshot.
It generates the complete exact UDM plan as the desktop user and tests default Polkit
denial without package mutation. `savevm reviewed` captures guest RAM plus qcow2 disk,
retaining the boot, process start times, logind session and machine identity across the
gate. There are no external backing files. The immutable seven-day snapshot artifact
contains the disk, source/seed ISOs, VM UUID, full baseline and review manifest.

Review **baseline.json** (all package versions, architectures, origins, dependencies,
conflicts and byte estimates), **baseline.png**, **denial.json**, **snapshots.txt** and
**review.json**. Record the source SHA, preparation run ID, manifest SHA256 and plan
digest. Artifact expiry requires a new preparation and review. Do not approve an
unseen transaction or reuse a digest from the older container simulation.

A separate deliberate `stage=accept` workflow dispatch with `review_run`,
`review_sha256` and `plan_digest` is the explicit administrator approval of that exact
snapshot transaction and the destructive disposable-guest tests described below.
Generic permission to run CI is not that approval. No automatic dispatch or PR event
can install. Missing digests, wrong revision/run provenance, changed files or changed
guest transaction fail closed. This is the digest-bound manual workflow alternative
to a protected GitHub environment; it does not assume required reviewers are configured.
Only authorized repository Actions operators can dispatch it. Keep that permission
restricted to humans authorized to approve installation.

Acceptance restores RAM/disk, checks the same baseline identities and re-resolves the
full transaction before adding a temporary Polkit test rule restricted to the desktop
user, installed helper path and exact command/digest. It exercises
`udm-app packages install DIGEST` → pkexec → the root-owned helper, never direct apt
KDE installation or a forged PKEXEC_UID. This automated administrator rule tests real
Polkit/helper authorization; it does **not** validate an interactive auth_admin prompt
or password dialog. Default deployed policy is unchanged. The rule is removed after
each case and is absent from the review snapshot.

## Cases and evidence

Each destructive case starts from a separate copy of the reviewed running snapshot:

- Stale digest: actual authorized helper rejects it before commit; inventory unchanged.
- Download failure: isolated guest network namespace has no uplink; actual APT fails.
- Native dpkg failure: a fixed, pre-provisioned dpkg pre-invoke hook exits 42 only when
  its test marker is enabled. This establishes native dpkg failure handling, not a
  maintainer-script failure after partial configuration.
- Interruption: observe a real dpkg process and kill its operation process group and
  dpkg; require a durable interrupted record and blocked retry. No observed dpkg
  process means failure, never a simulated pass.
- Verification failure: after a real successful installation, make the disposable
  guest launcher non-executable and require verify to report not ready. This tests
  post-install detection; helper journal verification failure is covered separately
  by the existing injected unit test, not claimed as a native maintainer-script case.
- Success: require actual target verification, one ready operation with approved
  digest, clean dpkg audit, executable launcher and Debian wrapped Wayland session.
  Run PR #12's real KWin/plasmashell QPainter test under another user with private
  D-Bus/runtime state. Preserve the original desktop/session and LightDM throughout.

After each case the reviewed administrator recovery is restoring the approved VM
snapshot, not package repair. A final restore must reproduce the original inventory,
transaction and running identities. No `dpkg --configure -a`, fix-broken, downgrade,
uninstall or blind journal deletion is automated. Native package repair, interactive
Polkit authentication and full guest power-loss remain separate acceptance evidence.

Artifacts retain JSON outcomes, full package inventories, VM/image/source identities,
process/session/display-manager baseline, Polkit stdout/stderr, native APT/dpkg logs,
operation records, original desktop screenshots and Plasma screenshot/log/result.
Failures retain diagnostics and fail the job. `acceptance.json.complete=true` only
follows all assertions and final snapshot recovery. No physical GPU/input, native
login, compositor takeover, display-manager restart, logout or window-migration claim.
The service-start guard is not a maintainer-script sandbox; real continuity assertions
are mandatory and can fail even if Cargo or container CI passes.

## Acceleration and reproduction

GitHub [does not officially support nested virtualization](https://docs.github.com/en/actions/concepts/runners/github-hosted-runners).
Acceptance also requires the reviewed QEMU binary hash, host architecture and
acceleration mode; tooling changes require a fresh preparation/review. The workflow exposes only the KVM device to the tooling container when present.
A bounded real QEMU initialization probe must succeed before selecting KVM; otherwise
the guest uses TCG and records the probe error. Host device permissions are not changed. `review.json`
records actual selected acceleration and full preparation duration; serial logs retain
boot/provisioning progress. Default bounds: 60-minute preparation, 120-minute job.
TCG performance must be measured before claiming hosted-runner feasibility. Select
`udm-disposable-kvm` only on an explicitly configured disposable Linux runner with
Docker, at least 8 GiB RAM and adequate artifact/disk capacity; do not attach a primary
desktop or the offline CachyOS miix320. GitHub's unaccelerated run is an experiment,
not a supported nested-virtualization promise.

Local focused check: `python3 -m unittest discover -s tests/vm -v`.
For Linux with Docker, build the Rust binary and then:

```sh
docker build -t udm-vm-tooling tests/vm
mkdir vm-state
docker run --rm --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src="$PWD/vm-state",dst=/state udm-vm-tooling \
  prepare --source "$(git rev-parse HEAD)"
```

Add `--device /dev/kvm` only after checking acceleration. Never run `accept` before
reviewing and explicitly approving its exact manifest and transaction digests.
