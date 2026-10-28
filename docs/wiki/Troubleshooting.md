# Troubleshooting

A failed read of a Linux release file or session entry is an error. Check file access
without using sudo to run UDM. Missing standard session directories produce an empty
inventory. An unknown APT result may mean missing/stale metadata or a failed query;
UDM never refreshes repositories. Unsupported means that host/release has no validated
query adapter. Include the revision, distribution and sanitized report in a bug report.

For experimental v0.2 package operations, a changed digest requires a new plan
and review. Existing service policies, pending recovery, required upgrades, removals
or display-manager changes block installation. An administrator should inspect the
operation record and APT/dpkg logs after failure. UDM does not automatically uninstall,
downgrade or repair packages. A partial installation may require manual recovery or
restoring the disposable VM snapshot. An interrupted service-start guard also needs
administrator inspection before normal service management resumes.
