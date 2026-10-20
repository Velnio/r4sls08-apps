# Velnio Installer — experimental App 1.0.15

Installs the bundled Velnio 0.2.2 integration into Home Assistant. Requires Home Assistant 2026.9.1 or newer and an AMD64 or ARM64 installation supporting Apps. The App uses manual start and can restart Home Assistant Core during installation. Leave the product option set to `velnio` for Velnio installations; the separately bundled R4 payload does not establish a shared bus or migrate R4 configurations.

## Install

Add `https://github.com/Velnio/r4sls08-apps` to the Home Assistant App Store repositories. Refresh the store, select **Velnio Installer**, install App **1.0.15**, and start it with the default options. Allow the initial Core restart to complete. Check the App log for `READY: installed` and verify integration version **0.2.2**. Stop and start the App once more; an unchanged installation should report `READY: unchanged` without restarting Core. Stop the App when finished. A completed public-route test is recorded separately in the release receipt; this guide alone is not a test result.

Do not remove or replace an existing R4 Installer App to install this separate Velnio App. After code installation, configure Velnio through Home Assistant's integration flow using the documented P8/V10 topology. Firmware updates and hardware flashing are outside this release.

## Defaults and recovery

Defaults are `health_timeout: 180`, `retry_failed_release: false`, `backup_count: 5`, `product: velnio`, `rollback_to: ""`. Core restart has a separate request budget; changing the health timeout is unnecessary for the qualified first-start path. Keep the default no-retry behavior after an uncertain operation; preserve the logs and inspect the installed version before attempting another start.

The installer keeps a bounded history of integration-code backups. To roll back integration code, stop the App, select a verified existing backup identifier in `rollback_to`, and start it. Read the result, then clear `rollback_to` before a later normal upgrade. Never guess an identifier or select the same rollback repeatedly after an uncertain result. Rolling back integration code does not downgrade the App image, revert device configuration, or restore the entire Home Assistant system. Protect existing backups before an install if the configured retention limit would remove them. A separate full-system backup and recovery plan remains the operator's responsibility.

## Experimental limits

This release is for controlled evaluation. It is not stable 1.0 or completed pilot acceptance. U4 remains open: physical P8/V10, adapter/UART/driver timing, echo/event behavior, capacity and sustained fault/soak qualification have not been accepted. Hardware performance and support limits are not established by installer tests.

U12 scheduling has offline software coverage; its physical acceptance remains open. Optional temperature entities (U16) and the complete port/device/event-service health entities (U23) remain unfinished. Firmware v1.1 features and passive HealthAgent expansion are outside this release. Do not rely on these unfinished capabilities for monitoring or control. The standalone runtime has no APK package manager; image maintenance requires a replacement image.

Previous isolated tests qualified code installation under a new App slug on ARM64 and AMD64. They were clean Velnio-target tests on existing HA fixtures, not factory-new entire HA systems. The earlier missing historical full backup and unverified historical archive were not recovered by those tests; whole-system preservation is not claimed. Current public availability and anonymous retrieval must be read from the separately published release receipt.

## Sources and licenses

The matching release contains two exact architecture-specific source-material archives, integration ZIP and manifest, notices, and SHA-256 checksums. These include installer source/build inputs and upstream source materials. Historical prepare-only and queued-CI metadata inside immutable source archives remains historical; the current release decision and verification receipts describe publication and observed outcomes. Source materials do not assert independent binary reproducibility or blanket legal certification.

Mijoo s.r.o. licenses the identified first-party Velnio/installer and included R4 code and ten graphics under Apache-2.0. Upstream components retain their individual terms. No additional trademark rights are granted. See the release's LICENSE, NOTICE and third-party notices. Firmware and hardware designs are excluded.

## Support and first evaluation

The operational release owner is **Mijoo s.r.o.** Report problems and escalate experimental-release issues through [GitHub Issues](https://github.com/Velnio/r4sls08-apps/issues). The first evaluation is scheduled for 14 calendar days after actual public publication; the final release receipt supplies the publication time and corresponding evaluation date. No response-time SLA, staffed support hours or guaranteed hardware support is promised. Include App/integration versions, architecture, expected and observed behavior, and sanitized diagnostics. Remove credentials, personal information and private network details before posting a public issue.

Matching experimental release: https://github.com/Velnio/r4sls08-apps/releases/tag/velnio-0.2.2-app-1.0.15-experimental.1
