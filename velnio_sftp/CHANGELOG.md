# Changelog

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
