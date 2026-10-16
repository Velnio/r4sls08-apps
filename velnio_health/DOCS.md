# Velnio Health Agent pilot

The default metrics-only profile collects Core API status, Supervisor health/support
and free space on the Supervisor data volume. The app also composes an opt-in
heartbeat runtime with canary, required service, critical entity and device checks.
Version 0.3.0 has qualified synthetic image coverage for metrics, heartbeat and
optional host metrics on both supported architectures. Real host rollout and
native acceptance for this version remain pending.
No HA service calls, repairs, backup/restore, Docker socket, host PID/proc or hardware
capabilities are required.

The app requests `homeassistant_api:true` and `hassio_api:true` with role `default`.
Supervisor injects its token; it is never printed or written to a new file. Only
GET `/core/api/`, `/supervisor/info`, `/host/info` are used by the metrics collectors.
The enabled profile additionally reads explicitly bound Core entity states.
These are application-enforced restrictions: HA's Core permission is broader
than these read routes. There is no claim of a server-enforced read-only Core
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
The image `ghcr.io/velnio/velnio-health-agent:0.3.0` remains private; Supervisor's
existing GHCR registry account must have read access to this package. No token
belongs in the catalog, app options, URL, Git or issue tracker. If access fails,
stop and resolve that specific registry permission before installing.

Version `0.3.0` is published as a qualified private image, and this catalog
promotes its authenticated metadata artifact. Its private source tag is
`health-v0.3.0` in `Velnio/velnio-backup`. Catalog publication does not establish
real host source freshness or native pilot acceptance.
The pinned CI workflow builds a wheel/context once, tests amd64 and arm64 images
with disposable data volumes and no network, and checks non-root operation,
authentication, graceful stop and token continuity. The pushed immutable index
must match both tested image config digests. Existing version tags are refused;
package visibility must remain private. Promotion uses only the successful
workflow artifact's config.json, DOCS.md and CHANGELOG.md, with publication-status
prose corrected in the public docs. Dockerfile, wheels,
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

## Optional heartbeat profile and qualification

`heartbeat_enabled` defaults to `false`; disabled startup does not read the private
heartbeat profile or handoff. Enabled startup requires strict private
`/data/agent/heartbeat-profile.json` and its local handoff reference, with approved
required-check bindings, both exact role plan keys and an independently approved
HTTPS origin/IP. Custody checks reject unsafe ownership, permissions and links;
private inputs and provider URLs never belong in app options or the public catalog.
The roles are `agent_alive` and `local_functional`. Required producers feed accepted
generations and a cycle barrier; independent senders sample only current evidence.
Close fences further attempts and both sender joins share one five-second shutdown
budget. Stop/start creates a new cycle owner and does not replay functional success.
A retained metrics token or HTTP acknowledgement does not prove functional health.

Release and qualification tools accept
`--requested-profile {metrics_only,heartbeat_enabled,host_metrics_enabled}`;
the helper CLIs default to `metrics_only`.
Legacy original build records without `profile_coverage` qualify only metrics-only.
Enabled qualification requires coverage retained inside the original authenticated
build artifact, with kind `original_image_smoke`, the same source commit and both
exact amd64/arm64 tested image config digests, and ordered profiles
`["metrics_only", "heartbeat_enabled"]`. Host qualification requires cumulative
coverage `["metrics_only", "heartbeat_enabled", "host_metrics_enabled"]`. Explicit
malformed coverage fails closed for every request. A qualifier consumes coverage
only from the original authenticated artifact; local sidecars, environment flags and source presence
cannot augment it.

Release dispatch accepts `requested_profile`, defaulting to `host_metrics_enabled`.
Tag pushes for `health-v0.3.0` select `host_metrics_enabled`; `health-v0.2.0` selects
`heartbeat_enabled`, and other versions retain metrics-only selection. Both
platform smoke commands must finish successfully and write their original
reports after cleanup. Capture accepts explicit
`--amd64-report` and `--arm64-report` paths, checks each report's exact schema,
source commit, version, platform, tested config and matching profile list, then
aggregates coverage into `build-evidence.json`. The original artifact remains
exactly two files: `build-evidence.json` and `build-manifest.json`. Missing or
mismatched reports cannot create enabled coverage. Metrics-only smoke cannot prove
enabled coverage; legacy artifacts remain unqualified for enabled requests.
Profile requests also reach the read-only existing-artifact qualification and
metadata-only catalog export paths. Per-platform reports are intermediate private
build inputs, not extra public catalog metadata.

The published 0.3.0 image passed the original network-isolated metrics, heartbeat
and host smoke profiles on amd64 and arm64 (ARM64 under QEMU). Synthetic image
coverage does not establish real host freshness or native acceptance. Native
manifest/custody/watchdog/lifecycle, A14 VPN-off/WAN-on,
A31 Core outage, A40 TLS/provider receipt, A41 outage/restart/no replay and A61 CM5
budget still require separate scoped evidence. Full VELN-68/69 remains open.
Authenticated central accepted-cycle consumption is a separate unadopted design;
an in-process slot, provider last_ping or two polls do not prove two healthy cycles.

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

## Optional host metrics (0.3.0)

`host_bindings` defaults to `{}`. Existing options that omit it remain compatible.
The nested schema follows the [official app options/schema syntax](https://developers.home-assistant.io/docs/apps/configuration/#options--schema).
Its only fields are `source_profile`, `cpu_utilization`, `memory_available`,
`memory_used`, `temperature`, and `boot_timestamp`; each sensor is optional.
The accepted profiles are `core-2026.9.3-haos-systemmonitor` and
`core-2026.10.1-haos-systemmonitor`, supported by matching official source comparisons. Selecting a
profile asserts a separately qualified official HAOS System Monitor source;
entity names and units alone do not qualify it. Unknown keys, wrong profiles,
non-sensor entities and duplicate bindings fail closed at startup.

Host entity bindings require `heartbeat_enabled: true` and the already approved
private heartbeat profile/handoff. Bootstrap reuses its numeric Supervisor
StateAPI and injected Supervisor token. No extra credential, dial-address option,
permission or file is introduced. Host-only startup without that approved route
fails closed. Existing heartbeat checks and required producers are unchanged.
Preserve the installed private heartbeat inputs, metrics token and selected
NetBird listen address; the empty source default is not an instruction to replace
an enabled pilot's options.

Leave bindings empty until the exact Core/System Monitor source, HAOS scope,
integration/entity ownership, permissions and source freshness are qualified.
Dynamic readings require fresh `last_reported`; a REST read cannot renew stale
source evidence. Temperature is optional. CPU/RAM/boot sensors are not enabled
or discovered by this app. No host value is guessed or replaced with zero.

The published 0.3.0 release retains cumulative `metrics_only`, `heartbeat_enabled`
and `host_metrics_enabled` coverage in the original authenticated build artifact,
bound to its source and both exact image configs. The host probe used the installed
application composition, scheduler and authenticated export handler with synthetic
Core/System Monitor inputs and blocked sockets. It covered CPU, RAM, temperature,
boot/uptime, disk metrics, unit conversions and stale/absent omission. This image
evidence does not activate host entities or prove their real freshness; the
scoped native rollout and host source acceptance remain pending.
