# First launch

Run `cargo run --locked -p udm-app` from the source checkout. UDM prints a JSON report
and exits; there is no graphical window yet. Look at `host`, `sessions`, `desktops`
and `warnings`. A session entry can exist even if its launcher is broken. No desktop
is selected, started or stopped by this command.
