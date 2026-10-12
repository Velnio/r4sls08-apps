# Velnio Health Agent pilot

This app packages existing65/66/67 modules. Its live scope is Core API status,
Supervisor health/support and free space on the Supervisor data volume. It does
not yet compose canary, entity/device checks, heartbeat68, or full lifecycle69.
No HA service calls, repairs, backup/restore, Docker socket, host PID/proc, hardware
capabilities, external receivers or persistent source telemetry are required.

The app requests `homeassistant_api:true` and `hassio_api:true` with role `default`.
Supervisor injects its token; it is never printed or written to a new file. Only
GET `/core/api/`, `/supervisor/info`, `/host/info` are implemented by our client.
These are application-enforced restrictions: HA's Core permission is broader
than those three requests. There is no claim of a server-enforced read-only Core
token. Default Supervisor role allows info routes; manager/admin is unnecessary.

The pilot profile is Supervisor2026.09.3. Other versions fail the Supervisor
collector as unsupported; requalification is needed before treating host fields
as qualified on another version. Core2026.9.3's upstream status handler returns
the same strict `{"message":"API running."}` contract used by our Core collector.
See [Core source](https://github.com/home-assistant/core/blob/2026.9.3/homeassistant/components/api/__init__.py)
and [Supervisor role source](https://github.com/home-assistant/supervisor/blob/2026.09.3/supervisor/api/middleware/security.py).

## Build and delivery

The public HA app catalog is [Velnio/r4sls08-apps](https://github.com/Velnio/r4sls08-apps).
Add that repository in HA's App Store and select **Velnio Health Agent**.
The image `ghcr.io/velnio/velnio-health-agent:0.1.2` remains private; Supervisor's
existing GHCR registry account must have read access to this package. No token
belongs in the catalog, app options, URL, Git or issue tracker. If access fails,
stop and resolve that specific registry permission before installing.

Private source releases use tag `health-v0.1.2` in `Velnio/velnio-backup`.
The pinned CI workflow builds a wheel/context once, tests amd64 and arm64 images
with disposable data volumes and no network, and checks non-root operation,
authentication, graceful stop and token continuity. The pushed immutable index
must match both tested image config digests. Existing version tags are refused;
package visibility must remain private. Promotion uses only the successful
workflow artifact's config.json, DOCS.md and CHANGELOG.md. Dockerfile, wheels,
source and private build evidence never enter the public catalog. Installer
releases preserve this app's metadata and version independently.

`python scripts/package_health_app.py --output /private/operator/new-context`
remains a local artifact builder for review/debugging; it neither deploys nor
starts Docker. Its source/artifact manifest captures the exact input and wheel
bytes and rejects source changes during packaging. Native HA delivery uses the
prebuilt private image; do not paste the generated context into HA's terminal.
The image uses the pinned multiarch Python base reference in Dockerfile. CI
synthetic image evidence does not replace native HA permissions and collector
acceptance on the approved target.

## Pilot configuration and custody

Default `listen_address:127.0.0.1` exposes no remote listener. A separately
approved pilot may set its actual NetBird IPv4; only loopback or100.64.0.0/10 is
accepted. Never bind0.0.0.0, LAN IP or publish a host port. The app uses host
network solely to bind the existing overlay address, without NET_ADMIN/NET_RAW
or changing routes/DNS/ACL. If that address is absent, startup fails closed.
NetBird must be running before an overlay start; boot remains manual in the pilot.

Root bootstrap prepares only a new private `/data/agent` directory and token,
then clears supplementary groups and sets UID/GID65532. Existing unsafe modes,
owners, hardlinks or symlinks fail closed; no recursive chmod/chown repair occurs.
The service cannot run as root. `/data/agent/metrics.token` is stable0600 state,
generated once and never logged. It has to be securely delivered to the approved
Prometheus credential file later; no token belongs in Git, tracker or browser URL.

GET `/live` and `/ready` report agent-loop progress/readiness, not house health.
GET `/metrics` requires exactly one matching Bearer header; unknown paths and
control methods are rejected. Collection runs independently every30seconds;
scrapes read snapshots. Core failure must leave the agent loop running.
CPU/RSS/p95 targets and encrypted cross-peer scraping require their own evidence.

## Acceptance and rollback

Before install, record the exact context/wheel/base digests, target architecture,
Supervisor/Core profile, selected listener address, previous installed-app and
port state, capacity and user authorization. Do not modify another app or restart
Core/Supervisor/host. Install/start only this catalog app. Verify effective UID/GID,
AppArmor/no Docker mounts/capabilities, exact listener, missing/wrong/duplicate
token401 and valid token200 without printing secrets. Compare app lists and
check Core still runs; test only this app's stop/start with token continuity.

Rollback first stops only this app, removes its listener and restores any changed
options. Preserve private token/data and evidence; uninstall/data deletion is a
separate explicit step. No `prune`, `down -v`, Core restart or NetBird change.
Fleet/site identity is not invented by this app. A future accepted fleet render
uses the existing stable site_id and approved overlay target/reference map; do
not relabel synthetic fixtures as a real monitoring release.
