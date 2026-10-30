# Fresh VM tooling image

Run **Build fresh VM tooling image** manually in Actions. While this PR is unmerged,
an explicit `[vm-tooling-image] ` commit on `ci/debian13-snapshot-vm` also triggers it
only when the workflow, tooling loader or VM Dockerfile changes. Ordinary pushes,
pull requests and schedules never build the image. The manual Actions entry becomes
available on the default branch after integration; the narrow push path permits
validation before merging.

The manual trigger is already callable on this branch:

```sh
gh workflow run vm-tooling-image.yml --ref ci/debian13-snapshot-vm
```

Each invocation pulls the current Debian 13 base, disables layer-cache reuse,
refreshes APT metadata, upgrades installed packages and installs the existing QEMU,
Python, ISO, curl and certificate prerequisites. Updates stay within Debian 13.
It does not build the Rust application or install KDE; those are separate guest/
application operations. No registry credentials, local Docker daemon or guest
installation approval are needed to build this GitHub-hosted tooling artifact.

The job exports a gzip-compressed Docker image, exact package inventory, image
inspection metadata and SHA256 checksums. It removes the image tag, reloads the
archive, checks the image identity and smoke-tests all prerequisite tools. Artifacts
are `udm-vm-tooling-image-ATTEMPT` and small `udm-vm-tooling-metadata-ATTEMPT`, retained
for seven days. Workflow reruns rebuild with current dependencies and get distinct
attempt artifacts, preserving earlier reviewed bytes.

## Latest successful image policy

Every new VM job resolves the newest **successful** run of this repository's image
workflow at job startup, including its latest successful attempt. It validates run,
source, recipe, architecture, archive hash and loaded Docker image identity. It does
not use a mutable `latest` tag or fall back to an older image when the newest
artifact is missing/expired or its recipe differs. Build a fresh image in that case.
This means latest published dependencies, refreshed whenever the image action runs;
it does not silently rebuild on every ordinary CI push.

Preparation records the full image identity in `review.json`. Acceptance resolves
the latest successful image again and requires it to equal the reviewed image. A
newer build after review stops acceptance before starting a guest; prepare a new
snapshot and obtain exact approval. Older snapshots without an image binding must
also be prepared/reviewed again. Existing accepted historical evidence is unchanged.
Image generation never authorizes a package transaction, and no guest/host package
repair is automated. Snapshot files, QEMU hash, CPU, acceleration and guest plan
checks remain in place. This change does not mitigate the reported guest CPU flaw.

To use an exported image outside CI, download and extract its artifact, then:

```sh
sha256sum --check SHA256SUMS
docker image load --input udm-vm-tooling.tar.gz
```

The loaded tag is `udm-vm-tooling:artifact`; its default entrypoint expects the
repository mounted at `/source`, as documented in [the VM protocol](README.md).
Rust, native APT simulation and the separate Plasma container check retain their
own prerequisites; this image is the shared VM tooling runtime.
