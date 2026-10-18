# Changelog

## 0.1.1 — 2026-10-18

- Bundle integration 0.1.1 with the reviewed lifecycle correction: register the
  backup-agent listener synchronously and defer discovery refresh until the
  config entry reaches the loaded state.
- Pin the immutable integration source and reproducible ZIP checksum. Preserve
  the existing private-image, Core-build and exact smoked-image release gates.
- Publish the private 0.1.1 image after isolated install/update qualification on
  amd64 and arm64. [Release run 39143509215](https://github.com/Velnio/velnio-backup/actions/runs/39143509215)
  verified private visibility and the exact smoked platform configs. Multiarch
  digest: `sha256:de630a2bd0bfb98d84f3db6b75a9c9b0b0fa8cb070ef83b56a82440b94fc955e`.
- Metadata-only catalog entry updated to 0.1.1. No Home Assistant deployment, SMB or monitoring
  change was performed.

## 0.1.0 — 2026-10-17

- Separate one-shot app for installation and updates of the native Velnio SFTP
  integration 0.1.0.
- Read-only default status and preview until an explicit Core restart is enabled.
- Verified bundled payload, fixed component scope and supported Core-build gate.
- Existing exact installation adoption; edited/newer versions and unresolved
  transactions fail closed.

The private multiarch image passed isolated atomic install/update qualification
on amd64 and arm64. A real encrypted configuration backup through the native
integration passed transfer/readback and existing recovery-secret verification.
The installer app has not been deployed on Home Assistant; its first real
Supervisor/Core lifecycle remains a separate pilot step. Restore is not yet
qualified.
