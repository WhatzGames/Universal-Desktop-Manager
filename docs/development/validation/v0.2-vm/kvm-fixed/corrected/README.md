# Corrected interruption observer: same approved transaction

The human reaffirmed approval to finish the same GitHub-only suite after the interruption observer defect was explained. The corrected source only changes the VM observer/regression and evidence documentation; Rust/helper/Polkit/package policy are unchanged. The entire transaction object is byte-for-byte semantically identical to [the approved transaction](../transaction.json), including state fingerprints and digest. No additional package or test scope is authorized.

- Source: `0b37612cb8fd6ae0f3bdd85841be5f4488c7766e`.
- Preparation: [40973901267](https://github.com/WhatzGames/Universal-Desktop-Manager/actions/runs/40973901267), passed; 119.715 seconds with same-runner restore proof.
- Manifest SHA256: `dc906754152d6a2d8d3b046538a25b832d38b44da939ae16f39eb8be44430a77`.
- Transaction: `ed20b81bb265c6549f47ecd5b978ac1affe0b79e694ed25da8f1e62381266fa9` (unchanged).
- KVM, `software_only: false`, enforced CPU `Westmere-v1,phys-bits=40,enforce`; same QEMU hash and Debian image as the independently restored predecessor.

[Manifest](review.json), [baseline/mitigation report](baseline-summary.json), [denial](denial.json), [restored desktop](snapshot-restore.png). Guest speculative-store-bypass vulnerability and all prior limitations remain. Acceptance revalidates every file, source, QEMU, CPU, acceleration and full guest plan; incompatible state fails closed. The first approval workflow is not rerun: a new signed approval-only transition binds the corrected source and new snapshot under the human's reaffirmed unchanged scope.
