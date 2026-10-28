# Troubleshooting

A failed read of a Linux release file or session entry is an error. Check file access
without using sudo to run UDM. Missing standard session directories produce an empty
inventory. An unknown APT result may mean missing/stale metadata or a failed query;
UDM never refreshes repositories. Unsupported means that host/release has no validated
query adapter. Include the revision, distribution and sanitized report in a bug report.
