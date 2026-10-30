# Known limitations

No GUI, desktop activation, compositor or live switching exists yet. The v0.2
Debian 13 installer is experimental. There is no automatic package rollback.
Other distributions have unsupported package queries. Session entries can be stale.
Xwayland does not migrate windows between desktops. Future nested desktop sessions
retain applications in their original session; native login may require logout.

The [approved Debian 13 KVM test suite](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40975763374) passed real installation,
documented stale/download/dpkg/interruption/verification failures, original
XFCE/LightDM process and session continuity, isolated KWin/Plasma rendering and final
snapshot recovery. It added exactly 579 reviewed packages without removing packages
or changing existing versions. This validates the disposable test guest, not a
supported release or physical hardware. Ordinary pushes cannot trigger installation.

Interactive auth_admin password prompting, partially configured maintainer-script
recovery, native package repair, full guest power loss and physical GPU/input remain
untested. The native dpkg failure hook runs before unpacking; interruption proves
a real mutating command/journal interruption, not every maintainer-script state.
Maintainer scripts remain privileged; policy-rc.d is not a sandbox. Recovery restores
the reviewed VM snapshot. No primary desktop or host package change was tested.

The fixed enforced KVM CPU model passed independent-runner restoration, but does not
guarantee compatibility with every runner. The test guest reports speculative-store-
bypass vulnerability; this public-data disposable VM is not production security
validation. Source/manifest/transaction changes remain review boundaries.
