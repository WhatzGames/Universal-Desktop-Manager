# Supported desktops

| Capability | Current status |
|---|---|
| Standard X11/Wayland session-entry inventory | Implemented; entries do not prove launchability |
| KDE Plasma Wayland catalog item | Always listed, including when no entry is found |
| Debian 13 KDE package query | Read-only local APT candidate query; empty/stale metadata can give unknown |
| CachyOS / Arch package query | Unsupported; host and session inventory smoke-tested on CachyOS |
| Desktop installation or activation | Not implemented |
| Live switching and window preservation | Not implemented |

Hardware smoke testing on one CachyOS machine does not establish general desktop or
GPU compatibility. Full KDE Wayland dependency checks remain unverified.
