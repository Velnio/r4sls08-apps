# Velnio Installer App 1.0.18 / full integration 0.4.1

This updates the full `velnio` integration. It preserves its Settings menu,
branch inventory, quick bindings, LED feedback, profile controls, settings
transfer and diagnostics. It supports addressed event transport for P8 firmware
0.3.0 and bootloader-enabled application firmware 0.4.0. The bootloader
updater is outside this App release. It is separate from `velnio_smart_button`, the experimental prototype.

## Update

Use the existing Velnio Installer from
https://github.com/Velnio/r4sls08-apps in the Home Assistant App Store.
Refresh the store, update to **1.0.18**, then start the App with product
`velnio`. Updating the App image alone does not install integration code;
starting it performs the transaction and may restart Home Assistant Core.
Wait for `READY: installed`, then verify integration **0.4.1** and its Settings.
A subsequent unchanged start should report `READY: unchanged` without restart.
Stop the installer when finished.

Preserve existing installer options, backup retention and a recent HA backup.
Code rollback does not restore device flash or a full Home Assistant backup.
Do not enable automatic retries after an uncertain install; inspect the log
and installed version first. Existing R4 integration/configuration uses its
own product and physical branch and is not migrated by this release.

## Port ownership and prototype handoff

Only one integration or serial client may own each RS485 port. Disable the
experimental prototype entry and wait for its port to close before assigning
that same port to full Velnio. Preserve its journal/session authority; never
overwrite it with an old example journal or guess a smaller session counter.
Use the full integration's documented prototype import/branch recovery
flow with the actual saved configuration. Prototype import currently requires
a fresh destination inventory; it does not overwrite an existing full branch. Stop manual serial monitors before
enabling the production entry. Retain existing branch inventories and entity
identities; do not delete and recreate entries merely to upgrade code.

## Scope

P8 still recognizes single, double and hold gestures locally. The host reads
correlated batches and acknowledges exact events. Temperature and LED/profile
controls remain part of the full integration. Firmware is not flashed by this
App. Installer tests do not qualify 25–50 physical modules, cabling, termination,
relay response time or a universal 500 ms latency bound.

Requires Home Assistant 2026.9.1 or newer, Python 3.14, and an App-capable ARM64
or AMD64 installation. This remains an experimental release. Matching source
materials and legal notices are attached to the GitHub release. First-party
Apache-2.0 terms do not replace individual upstream licenses. The runtime has
no APK package manager; update it by replacing the App image.

## Defaults and recovery

Defaults are `health_timeout: 180`, `retry_failed_release: false`, `backup_count: 5`, `product: velnio`, `rollback_to: ""`. Core restart has a separate request budget; changing the health timeout is unnecessary for the qualified first-start path. Keep the default no-retry behavior after an uncertain operation; preserve the logs and inspect the installed version before attempting another start.

The installer keeps a bounded history of integration-code backups. To roll back integration code, stop the App, select a verified existing backup identifier in `rollback_to`, and start it. Read the result, then clear `rollback_to` before a later normal upgrade. Never guess an identifier or select the same rollback repeatedly after an uncertain result. Rolling back integration code does not downgrade the App image, revert device configuration, or restore the entire Home Assistant system. Protect existing backups before an install if the configured retention limit would remove them. A separate full-system backup and recovery plan remains the operator's responsibility.


## Sources and licenses

Mijoo s.r.o. licenses the identified first-party Velnio/installer and included R4 code and ten graphics under Apache-2.0. Upstream components retain their individual terms. No additional trademark rights are granted. See the release's LICENSE, NOTICE and third-party notices. Firmware and hardware designs are excluded.

## Support and first evaluation

The operational release owner is **Mijoo s.r.o.** Report problems and escalate experimental-release issues through [GitHub Issues](https://github.com/Velnio/r4sls08-apps/issues). The first evaluation is scheduled for 14 calendar days after actual public publication; the final release receipt supplies the publication time and corresponding evaluation date. No response-time SLA, staffed support hours or guaranteed hardware support is promised. Include App/integration versions, architecture, expected and observed behavior, and sanitized diagnostics. Remove credentials, personal information and private network details before posting a public issue.

Matching experimental release: https://github.com/Velnio/r4sls08-apps/releases/tag/velnio-0.4.1-app-1.0.18-experimental.1
