# Approved KVM acceptance passed — 2026-10-30

[Run 40975763374](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40975763374) passed the signed approval gate, all six native cases, isolated Plasma readiness and final snapshot recovery. [Complete harness outcome](acceptance.json), [independent evidence audit](checks.json).

Source `4d3c188b9a94166e1e50a4b7fbb34bfb6a830697`; signed owner approval-only commit `a508ea6fb41f7895b316687f10e6f33caca352bd`; preparation 40975306873; manifest `15eaf3fcb54f542beda9b57a9dc3b6c20d13cebe78cbf65d1c7d34fee55a9edc`; transaction `ed20b81bb265c6549f47ecd5b978ac1affe0b79e694ed25da8f1e62381266fa9`. KVM with fixed enforced CPU and exact reviewed QEMU/files/source. The human reaffirmed approval after observer corrections; the complete package transaction and suite scope remained unchanged.

| Case | Observed result |
|---|---|
| Stale plan | Real helper rejected changed digest; no journal/package changes |
| Download failure | Native APT network namespace failure; durable failed operation |
| dpkg failure | Native dpkg pre-invoke hook failed; durable failed operation |
| Interruption | Observed approved dpkg --unpack descendant; stopped native dpkg and killed its exact invocation parent chain; durable installing record survived and retry was blocked |
| Verification failure | Native commit completed, deliberate launcher permission fault made helper verification fail; clean audit, durable failed operation and explicit recovery advice |
| Success | Real Rust CLI → pkexec → root-owned helper; exactly 579 new packages, zero removals/changed existing versions; one ready operation for UID 1000 and approved digest; clean audit, launcher/session definition verified, no session activation |
| Plasma | Separate UID 1001; real KWin Wayland/QPainter, one desktop and panel, rendered wallpaper; [result](plasma/result.json) and [screenshot](plasma/plasma.png) |
| Final recovery | Reviewed RAM/disk snapshot restored; original complete transaction, inventory and XFCE/LightDM PID/start/session identities match |

Every case retained the original XFCE/LightDM baseline. [Installed desktop](install.png), [recovered desktop](recovered.png), [recovered identities](recovered-summary.json). Per-case summary JSON preserves operation records without duplicating the full approved plan; original capture SHA256 values bind full artifacts. Native successful-install APT/dpkg logs are retained here with ANSI/carriage-return/trailing-whitespace normalization; raw hashes/full original captures remain in the run's debian13-vm-evidence-accept artifact. No host packages or local VM installation were used.

This proves the documented disposable Debian guest suite, not a supported release or physical hardware readiness. Interactive auth_admin password prompting, partially configured maintainer-script recovery, native package repair, full guest power loss, physical GPU/input, native session activation and window migration remain untested/out of scope. The dpkg hook case fails before unpacking; the interruption test proves a real mutating command/journal interruption, not arbitrary points in every maintainer script. Recovery is snapshot restoration, not automatic APT rollback. Guest speculative-store-bypass vulnerability remains documented. PR #13/#14 stay draft/unmerged; issues #10/#11 and v0.2 stay open for review.

Plasma text logs also normalize trailing whitespace and KWin section separators; original file hashes are in checks.json and original bytes remain in CI artifacts.
