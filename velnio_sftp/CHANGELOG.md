# Changelog

## 0.1.2 — 2026-10-18

- Store retained transaction payloads outside `custom_components` so Core cannot
  discover an old copy as a duplicate `velnio_sftp` integration. New transactions
  use schema 2 journals and owner-only staging directories on the destination
  filesystem.
- Classify schema 1 legacy state read-only. Duplicate-domain remnants and
  unresolved transactions require operator reconciliation; no automatic legacy
  cleanup or retry is performed.
- Correct the installer defect found during the 0.1.1 pilot, which required
  operator recovery. Keep integration 0.1.1 and its immutable payload unchanged.
- Private multiarch release run `39152186344` verifies private package visibility
  and exact smoked linux/amd64 and linux/arm64 configs. Immutable index digest:
  `sha256:f702bb254fe3bacb21fe4e14fc16f3b479901008c7cd2d0f966a2a766cb182fd`. Source: `3329df5e35178e37ff9bbd2d891faa184a976bcb`,
  tag `sftp-app-v0.1.2`.
- Catalog metadata publication performs no Home Assistant deployment. Live 0.1.2
  upgrade and restore qualification remain separate.

## 0.1.1 — 2026-10-18

- Bundle integration 0.1.1 with the reviewed lifecycle correction: register the
  backup-agent listener synchronously and defer discovery refresh until the
  config entry reaches the loaded state.
- Pin the immutable integration source and reproducible ZIP checksum. Preserve
  the existing private-image, Core-build and exact smoked-image release gates.
- Publish the private 0.1.1 image after isolated install/update qualification on
  amd64 and arm64. Release run `39143509215`
  verified private visibility and the exact smoked platform configs. Multiarch
  digest: `sha256:de630a2bd0bfb98d84f3db6b75a9c9b0b0fa8cb070ef83b56a82440b94fc955e`.
- The initial metadata-only publication did not deploy to Home Assistant. A
  later 0.1.1 pilot exposed the retained-payload defect described above and
  required operator recovery. Publication did not change SMB or monitoring.

## 0.1.0 — 2026-10-17

- Separate one-shot app for installation and updates of the native Velnio SFTP
  integration 0.1.0.
- Read-only default status and preview until an explicit Core restart is enabled.
- Verified bundled payload, fixed component scope and supported Core-build gate.
- Existing exact installation adoption; edited/newer versions and unresolved
  transactions fail closed.

At the 0.1.0 release, the private multiarch image passed isolated atomic
install/update qualification on amd64 and arm64. A real encrypted configuration
backup through the native integration passed transfer/readback and existing
recovery-secret verification. The installer app had not yet been deployed to
Home Assistant at that release. The later 0.1.1 pilot and required recovery are
recorded above. Restore remains separately unqualified.
