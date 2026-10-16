# Velnio SFTP

Velnio SFTP is a separate, manually started app that installs and updates the
`velnio_sftp` integration in Home Assistant Core. Core continues to create,
encrypt, schedule and restore backups. This app is a delivery tool; it does not
transfer backups itself and does not need to keep running.

## Availability

App **0.1.0** uses the published private image
`ghcr.io/velnio/velnio-sftp-app:0.1.0`, qualified on linux/amd64 and linux/arm64.
Its immutable multiarch digest is
`sha256:31101884b6156d0526764d95536415da391d379592a60ff1003624148cc0e9fa`.
The [release qualification](https://github.com/Velnio/velnio-backup/actions/runs/38977251483)
records the committed source and exact tested platform image identities.

The catalog is [Velnio/r4sls08-apps](https://github.com/Velnio/r4sls08-apps).
Installation requires Supervisor's registry account to have
read/pull access to the private image. No GitHub token is needed in app options
or in the running app. Never put credentials in this repository or in logs.

The integration and app have separate versions. App 0.1.0 bundles integration
0.1.0. The delivery profile accepts only Core **2026.9.3** and **2026.10.1**;
other Core builds are refused. The existing native integration pilot was
verified on Core 2026.9.3. Integration compatibility with Core 2026.10.1 does not
qualify a NAS worker to process that version's backup archives.

## Controls

The app starts only when you press **Start**, performs one operation and exits.
Keep **Start on boot** disabled. The default configuration only reports status:

```yaml
operation: status
restart_core: false
health_timeout: 120
```

- `status`: inspect the bundled integration and the installed component; never
  replace Core files or restart Core.
- `install`: prepare the first installation. With `restart_core: false`, only
  preview and validation run; Core files remain unchanged.
- `update`: prepare an update of a recognized installation. With
  `restart_core: false`, only preview and validation run; Core files remain
  unchanged.
- `restart_core`: set to `true` only when you authorize installation/update and
  one Core restart. It has no write effect for `status`.
- `health_timeout`: seconds to wait for the post-restart Core/integration health
  result; accepted range is 10–300, default 120.

For an approved install/update, select the operation, set `restart_core: true`,
save and manually start the app. It verifies the bundled manifest/checksums,
Core build and installed component before atomically replacing only
`/config/custom_components/velnio_sftp`, then requests one Core restart.
A restart briefly interrupts Core automations and API availability. Choose a
suitable maintenance window. After reading the result, restore
`restart_core: false` and `operation: status` before another manual start.

An exact, unmodified manually installed integration 0.1.0 can be recognized and
adopted. Unknown, edited or newer installations are refused. There is no
automatic downgrade, automatic retry or rollback option.

If restart or health verification times out, the result is ambiguous, not a
successful installation. Do not repeat install/update. Preserve the app's data
and journal for explicit operator reconciliation before another write attempt.

## Scope and permissions

The app receives a read/write map of the Home Assistant configuration directory
at `/config`. Its implementation is limited to the fixed `velnio_sftp` component
and its own private app state. The mapping and Core permission are broader than
this application-level restriction; they are not a filesystem sandbox around
that one component.

It requests Supervisor API access with the `homeassistant` role to inspect Core
and request the approved restart, plus Core API access for post-restart entry
health. Supervisor supplies the runtime token; it must never be logged or
exported. The app exposes no listener, published port or ingress and needs no
host network, Docker socket, privileged mode or hardware capability.

The operation preserves existing `.storage`, SSH client keys, SFTP trust records,
SMB configuration, monitoring configuration and other integrations. It does not
create a backup destination/config entry, change a schedule, create a backup or
perform a restore. After first installation, configure **Velnio SFTP** through
Home Assistant's integration flow using an independently verified NAS host key;
then select it in native backup settings when separately approved.

App uninstall is not integration removal. Preserve private keys and trust
records until their separate retention/removal decision. Do not manually edit
trust storage or copy a restored identity into service without the required
external restore-fencing and revocation review.
