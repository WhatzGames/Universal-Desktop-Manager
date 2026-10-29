# Explicit Debian VM push approval

Ordinary pushes run normal CI only. Expensive VM preparation requires an integration
branch commit whose first line starts with `[vm-prepare] ` (or explicit manual prepare).
The separate TCG experiment requires `[vm-prepare-tcg] `; it is not run with normal
KVM preparation.
This marker never authorizes installation.

Installation has a separate, fail-closed push gate:

1. The branch already exists as `ci/debian13-install-approved`.
2. Exactly one non-merge, non-forced commit changes **only**
   `.ci/debian13-approval.json` (addition or modification).
3. The push actor, commit author and committer are the repository owner; GitHub
   verifies the personal commit signature.
4. The first commit-message line is exactly `Approve Debian 13 VM MANIFEST_SHA256`.
5. The JSON has exactly the example's fields, `approved: true`, exact source/run/
   manifest/transaction identities, and a boolean acceleration choice.
6. The preparation run succeeded in this repository using the stated source and an
   allowed preparation workflow. Its small review artifact must match the approved
   manifest SHA, transaction, source, restored-snapshot proof and acceleration before
   the expensive VM job is scheduled. KVM manifests must use the fixed portable CPU
   model; the original host-passthrough KVM snapshot is rejected.
7. The record is not a semantic repeat of the previous approved record; reruns of
   the push workflow cannot repeat installation. Running acceptance is never cancelled
   by a newer push; the approval workflow is serialized.

Wrong branch/path, creation/deletion/force pushes, mixed-file/multi-commit changes,
unsigned/wrong-owner commits, missing/false approval, mismatched review, ordinary
commit messages and workflow reruns cannot start installation. A whitespace-only
rewrite of an approved record is rejected. Fixes/retries need a new explicit approval
transition; do not use workflow rerun to repeat a package operation.

The example is deliberately **not approved** and is not the watched filename.
After a human explicitly approves the complete published transaction and exact guest
manifest, copy the example to the watched filename on the dedicated branch, update
it to the approved values and set `approved: true`. Commit only that file using the
exact title above and the existing personal signing/SSH setup. Do not combine a
workflow/code change with the approval commit. Publishing this mechanism or selecting
push-based execution is not package-transaction approval.

The workflow checks out the **reviewed source**, not the newer approval commit, for
VM execution. The original helper, package plan and snapshot remain frozen; their
hashes and guest state are revalidated before the actual CLI → pkexec → helper commit.
All execution is on GitHub's disposable Ubuntu runner; no local VM is required.
No new account token or main-branch merge is required for the push trigger.

No true approval record is shipped by the integration branch. A false record may be
used on the dedicated branch to prove rejection; it cannot schedule the VM job.
See [the full review packet](../docs/development/validation/v0.2-vm/README.md) and
[the VM protocol](../tests/vm/README.md). Maintainer scripts remain privileged and
installation acceptance is still pending actual approved execution.
