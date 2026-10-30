# Supported desktops

| Capability | Current status |
|---|---|
| Standard X11/Wayland session-entry inventory | Implemented; entries do not prove launchability |
| KDE Plasma Wayland catalog item | Always listed, including when no entry is found |
| Debian 13 KDE package query | Read-only local APT candidate query; empty/stale metadata can give unknown |
| CachyOS / Arch package query | Unsupported; host and session inventory smoke-tested on CachyOS |
| Debian 13 KDE installation | Experimental v0.2 candidate; approved disposable VM installation/failure/recovery suite passed |
| Desktop activation | Not implemented |
| Live switching and window preservation | Not implemented |

Hardware smoke testing on one CachyOS machine does not establish general desktop or
GPU compatibility. Native KDE installation and original desktop continuity passed in the disposable
Debian VM. Physical GPU/input readiness remains unverified.
