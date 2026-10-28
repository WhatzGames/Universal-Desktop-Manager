# Read-only discovery contract

Host: compile target OS/architecture; on Linux read /etc/os-release (fallback
/usr/lib/os-release), literal ID/VERSION_ID, detect standard /usr/bin package tooling.
No shell evaluation. An absent Linux release file or unreadable entry fails explicitly.

Sessions: read /usr/share/{wayland-sessions,xsessions}/*.desktop, only Desktop Entry
Type=Application with Name and Exec, excluding Hidden=true. Exec/TryExec are data only.
Localized names, XDG user overrides, executable validation, logind/session authority,
GPU readiness, storage and custom distribution paths are unimplemented. This is a
standard system-entry inventory, not proof that a session is installed or launchable.

KDE catalog always includes KDE Plasma Wayland, even with no discovered session.
Only Debian 13 uses /usr/bin/apt-cache policy kde-plasma-desktop under LC_ALL=C.
Candidate means present in local metadata, not installability or current remote state;
no candidate means unavailable; failed/ambiguous output means unknown. Other host/releases
report unsupported. No apt update, package resolution or changes. Full Wayland dependency
verification and bounded asynchronous command execution are future work. The local apt
query currently waits for process exit, so a broken local tool can delay the report.

Availability, entry presence, launchability and live-switch capability are separate.
Live-switch capability is always false. No user sessions or packages are modified.
