# Velnio SFTP

Velnio SFTP is a separate, manually started app that installs and updates the
`velnio_sftp` integration in Home Assistant Core. Core continues to create,
encrypt, schedule and restore backups. This app is a delivery tool; it does not
transfer backups itself and does not need to keep running.

## Availability

App **0.1.3** bundles integration **0.1.3**. The private image is
`ghcr.io/velnio/velnio-sftp-app:0.1.3`; its immutable multiarch digest is
`sha256:b13bb590cb7d74ebc05e325b44a2a133b42723095e331e0fe7aa6153b60a6265`.
[Release run 40240525760](https://github.com/Velnio/velnio-backup/actions/runs/40240525760)
verifies private package visibility and matches the published linux/amd64 and
linux/arm64 configs to the exact images that passed network-isolated smoke.
Those checks exercise actual Linux atomic install/update, a reconstructed
synthetic eleven-file managed receipt updating to the nineteen-file branded
payload, retained bytes, protected state, one restart, CURRENT no-op and refusal
to replay an ambiguous restart. The release source is
`c1e2c7f5f43c57737e3e3e727f57b59de5059e55`, tagged `sftp-app-v0.1.3`.

The integration profile pins source
`feb18e79fa50568349e59e113fd466a5213d84fd` and ZIP SHA-256
`a341b09d7f391358232048da5939b58ecaed25056c381d6aa8f4302b5419bdd6`.
Its closed payload contains eleven integration files and eight PNG brand assets.

Catalog publication does not deploy to Home Assistant. Earlier native
installation/recovery evidence applies to app 0.1.2/integration 0.1.1. Native
acceptance of 0.1.3 and the new key, rotation and exact Recorder recovery proofs
remain separate; the isolated image checks do not establish them.

The catalog is [Velnio/r4sls08-apps](https://github.com/Velnio/r4sls08-apps).
Installation requires Supervisor's registry account to have
read/pull access to the private image. No GitHub token is needed in app options
or in the running app. Never put credentials in this repository or in logs.

The integration and app have separate versions. App 0.1.3 bundles integration
0.1.3. The delivery profile accepts only Core **2026.9.3** and **2026.10.1**;
other Core builds are refused. The earlier native integration pilot was
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

An exact, unmodified manually installed integration matching the bundled 0.1.3
can be recognized and adopted. A recognized older managed installation with an
unchanged receipt can use `update`; a manually installed older version without
that receipt is refused as unknown and needs explicit operator reconciliation.
Unknown, edited or newer installations are refused. There is no automatic
downgrade, automatic retry or rollback option.

If restart or health verification times out, the result is ambiguous, not a
successful installation. Do not repeat install/update. Preserve the app's data
and journal for explicit operator reconciliation before another write attempt.


## Upgrading from 0.1.1

The ordinary 0.1.1 pilot upgrade retained an old integration payload beneath
`/config/custom_components`. Core discovered its duplicate `velnio_sftp` domain
even though the retained directory was hidden. The pilot required explicit
operator recovery; the immutable 0.1.1 image contains this defect. Its isolated
smoke result does not qualify its ordinary live upgrade path.

Version 0.1.2 stores new transaction stages in
`/config/.velnio_sftp-installer`, outside Core component discovery, with
owner-only directory permissions. Staging and destination must share a
filesystem. New transactions use schema 2 journals; schema 1 state is classified
read-only and is not silently rewritten as successful.

Keep `operation: status` and `restart_core: false` while checking an existing
installation. Preserve app data, the managed receipt, the journal and retained
payloads. A duplicate domain in any sibling beneath `custom_components`,
including a hidden copy, blocks install, update and adoption/current success.
Status reports reconciliation is required; it does not move or delete legacy
copies. There is no automatic legacy cleanup.

Do not retry an ambiguous 0.1.1 operation or delete evidence to make a check
pass. An operator must identify the approved active payload, preserve the old
payload and transaction evidence outside Core discovery, and separately
authorize any corrective restart. Verify the active files against the pinned
payload, exactly one original entry loaded, and its native backup agent healthy
before explicit reconciliation. Moving files alone does not prove Core recovery.

## Integration 0.1.3 transfer recovery

Uploads must contain exactly the advertised number of bytes. A short or oversized
stream fails before publishing its archive and metadata. If publication is
interrupted after the archive rename, an exact retry may finish publishing its
retained matching metadata only when the corresponding unique archive staging
path is absent. Foreign archives and conflicting metadata are refused.

A delete retry can finish removing matching metadata when the archive was
already removed by the interrupted delete. These transfer guarantees do not
establish successful restore, recovery-key custody or external identity fencing.
The separate offline dependency kit is pinned to Core 2026.9.3 ARM64; it does
not qualify offline recovery on Core 2026.10.1.

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
