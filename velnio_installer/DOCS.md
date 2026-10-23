# Velnio Installer

Add [Velnio Apps](https://github.com/Velnio/r4sls08-apps) to the Home Assistant App Store, then install **Velnio Installer 1.0.19**. Leave `product: velnio` selected and start the App. It transactionally installs **Velnio 0.7.3** under `/config/custom_components/velnio` and restarts HA Core when needed. A second start is an unchanged no-op.

Use **Settings → Devices & services → Add integration → Velnio**. Enter the dedicated serial port for that branch. Keep one integration owner per physical serial port. A P8 is identified by UID; its address and port are routing, so changing a name does not change device identity or existing entity IDs.

Configure button gestures in the board's quick bindings. Each LED can follow the state of a light or switch through **LED feedback**. Multiple buttons/boards can follow the same target, so their LEDs intentionally show the same target state. Directly controlling an LED temporarily overrides its output; the next target change restores synchronization without disabling feedback.

The qualified physical baseline is P8/V10 firmware 0.4.0 with HA Core 2026.9.4 on ARM64. Software tests use Python 3.14 and HA 2026.9.1; extracted-package checks also cover 2026.9.4. Installer images support ARM64 and AMD64. Other exact supported firmware profiles are admitted by the integration; unknown firmware/map/variant combinations are rejected. Firmware installation is separate and is never automatic during integration installation.

The installer preserves HA registries, integration data/options, inventory/session files and other integrations. Its rollback history covers integration code; it is not a rollback of Home Assistant's durable inventory/session authority. Do not replace that authority with an older snapshot.

Settings retain the existing defaults: `health_timeout: 180`, `retry_failed_release: false`, `backup_count: 5`, empty `rollback_to`. If a transaction fails, inspect the App log before retrying. Do not enable automatic retry to bypass an unresolved failure.

SFTP backup is a separate App/integration. Its destination credentials and host-key trust are configured separately; Velnio Installer does not repair or replace them. Support: [Velnio Apps issues](https://github.com/Velnio/r4sls08-apps/issues).
