# Settings

There is no settings screen or user configuration file yet. The default command
reads standard system release/session definitions and, on supported Debian 13 hosts,
local APT metadata. It changes none of those settings.

The v0.2 development branch also accepts explicit `packages plan`, `packages verify`
and `packages install REVIEWED_SHA256` commands. See [Installing Desktops](Installing-Desktops)
for their experimental status, administrator authorization and validation limits.
