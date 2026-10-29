# Fixed CPU KVM review candidate

Preparation and independent-runner restore passed. **The human approved this exact KVM suite; the first acceptance attempt stopped at an interruption-observer defect and is not validated.** This candidate replaces the withdrawn host-passthrough KVM snapshot. TCG is fallback-only.

| Identity | Exact value |
|---|---|
| Guest source | `fa95a619c62e5692661d0991a855249186ae4138` |
| Preparation run | [40971706077](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40971706077) |
| Manifest SHA256 | `7be97c3b7bcaa0a50cd4d1a39cff98dc6105f5a19d2010caad4d07aa6a91aef8` |
| Transaction digest | `ed20b81bb265c6549f47ecd5b978ac1affe0b79e694ed25da8f1e62381266fa9` |
| Disk SHA256 | `3a1ab44f0aa799e48948bef4db22fbe11ea0131997f05d4e764d63861d44d19e` |
| Acceleration | KVM, `software_only: false` |
| CPU | `Westmere-v1,phys-bits=40,enforce` |
| Independent restore | [40972477946](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40972477946), passed in 9.236 seconds |

[Complete transaction](transaction.json): **579 new packages**, 275,013,144 download bytes and 989,224,960 additional installed bytes estimated. No removals, upgrades or new display manager. The entire package selection, versions, origins and estimates match the historical transaction. Only two signed InRelease metadata fingerprints changed, so its old digest cannot authorize this candidate. [Comparison and restore checks](checks.json).

Preparation took 116.434 seconds, including original snapshot restore verification. Default Polkit denied the real CLI/pkexec request; inventory stayed unchanged. The independent job validated every manifest file, source, plan, QEMU binary hash, architecture, KVM and fixed CPU model before restoring RAM/disk. It asserted identical original desktop process/session identities, full transaction and package inventory. [Manifest](review.json), [baseline and mitigations](baseline-summary.json), [denial](denial.json), [independent result](cross-run-check.json), [restored desktop](cross-run-restored.png). Full original captures remain in the run artifacts. This is measured compatibility on these runners, not a guarantee on every future host; incompatible runners fail closed.

The common enforced CPU baseline retains guest kernel defaults. Its recorded report includes **spec_store_bypass: Vulnerable** and Spectre v2 retpolines with STIBP disabled. The v2 CPU trial refused unavailable spec-ctrl support; no feature-enforcement check was removed. This disposable public-data guest contains no supplied credentials; it is not production security validation. Host mitigations were not changed.

## Exact approval scope

Approve only the above source, preparation run, manifest and transaction, using copies of this reviewed GitHub-hosted guest. The suite runs the real CLI → pkexec → restricted helper installation, intentional stale-plan/download/dpkg/interruption/post-commit-verification failures, snapshot recovery, original desktop continuity and isolated Plasma readiness. Maintainer scripts run privileged; policy-rc.d is not a sandbox. Full suite results and duration remain unverified.

The [strict signed push gate](../../../../../.ci/README.md) requires one owner-signed approval-only commit on the existing dedicated branch. Ordinary pushes cannot install; repeat records and workflow reruns are rejected. Approval does not authorize local installation, host package changes, native package repair, primary-session activation or display-manager restart. The human approved the exact scope on 2026-10-30 (Europe/Berlin). Verified owner commit `e3439bea37bc644b498a92d60582e2cce0e11c07` changes only the approval JSON. The gate passed in [acceptance run 40973063920](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40973063920); [approval identity](approval.json). [First attempt evidence](first-acceptance/README.md). This is not a passing installation result. Review artifacts expire after seven days; missing or changed artifacts require a new review.
