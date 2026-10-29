# Original KVM snapshot: cross-runner restore rejected

[Read-only calibration 40969898313](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40969898313)
failed before guest capture or any installation/authorization. File/source/QEMU hashes
and KVM initialization passed. QEMU then exited with:

`Putting registers after init: Failed to set special registers: Invalid argument`

The original guest boot log identifies Intel Xeon Platinum 8573C; the new runner
is AMD EPYC 7763. Original source fc9df23 used `-cpu host`, binding saved CPU state
to its host feature set. QEMU [documents the cross-host limitation of passthrough](https://www.qemu.org/docs/master/system/qemu-cpu-models.html).
A same-job save/restore was therefore insufficient proof of cross-job KVM portability.

The old KVM manifest `24888a508b6575c42e8de9d9bfae490d5e0bce3f6b7161f8255b975ed6bcc621`
is withdrawn for the hosted push route. Its earlier preparation/same-host restore
results remain historical evidence, not a portable installation candidate. The push
gate now rejects host-bound KVM manifests. A replacement uses a fixed versioned CPU
model and physical-address width, with required-feature enforcement; its preparation
and independent-runner restore must pass before requesting new approval.

No KDE installation ran. The existing TCG preparation/restore evidence is unaffected.
