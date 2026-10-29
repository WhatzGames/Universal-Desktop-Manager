# Narrow push-gate validation

Executable gate source: `6b4559a46263974bff2dd949db725a6732c98d93`, GitHub Verified.
[Conditions and operator protocol](../../../../../.ci/README.md).
No real package transaction is approved or installed by this validation.

- [Integration push CI](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40965589506)
  passes and skips the heavy snapshot job. The separate TCG workflow is skipped too:
  ordinary integration pushes lack the explicit `[vm-prepare] ` marker.
- Bootstrapping `ci/debian13-install-approved` without the watched file created only
  normal CI, not an installation run.
- [Deliberately false approval](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40965706342)
  fails specifically with `Transaction is not explicitly approved`.
  The `approval` job fails and `acceptance` is **skipped**. This expected failure is
  evidence of denial, not a broken installer or successful installation test.
- [Documentation-only push](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40965924225)
  on that branch creates only normal CI. It does not trigger the approval workflow;
  the false record remains unchanged.
- Five new tests cover valid bound gate outputs, wrong branch/path, force/creation/
  deletion/mixed-file/multi-commit pushes, owner/signature/title checks, workflow
  reruns, semantic repeats, false/malformed records and wrong review/source/digests.
  Ten VM-focused tests plus sixteen helper tests pass. Cargo fmt, warning-free Clippy,
  locked build/test (seven Rust tests) and report smoke pass locally; PR CI passes.

The dedicated approval worktree is
`/Users/obedkooijman/CodexProjects/worktrees/Universal-Desktop-Manager-install-approved`.
Its actual watched record is deliberately `approved: false`; the integration branch
contains only a false **example** at another path. The signed true approval commit
is not created until the human approves the exact package transaction and VM.
The frozen guest source remains fc9df23; the workflow checks that source out rather
than executing guest code from the newer approval commit.

[Machine-readable checks](checks.json). Actual positive end-to-end push acceptance,
KDE installation, native failure/recovery cases and guest Plasma verification remain
pending exact human approval. No local installation route is needed for this trigger.
