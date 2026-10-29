# Known limitations

No GUI, desktop activation, compositor or live switching exists yet. The v0.2
Debian 13 installer is experimental: native resolution is tested, but snapshot-VM
installation, Polkit prompts, interrupted dpkg recovery and desktop continuity
are not yet validated. There is no automatic package rollback.
Other distributions have unsupported package queries. Session entries can be stale.
Xwayland lets X11 apps use a Wayland host; it does not migrate windows between desktops.
Future nested desktop sessions retain applications in their original session. Native
login switching may require logout; UDM promises no universal window migration.

A separate snapshot-VM CI candidate has prepared and restored a real Debian 13
XFCE desktop. KDE installation still requires approval and remains unvalidated. Its preparation stage
records the original desktop and exact package transaction. Installation requires
a separate explicit approval tied to that snapshot, source revision and transaction
digest. Passing the existing Plasma container check does not validate installation
safety, interactive authorization or preservation of your current desktop.
