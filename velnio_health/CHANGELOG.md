# Changelog

## 0.3.0 — qualified private image and catalog metadata

- Add finite optional System Monitor bindings to the HA app options schema;
  new installs remain disk-only with an empty binding map.
- Accept the additional exact Core 2026.9.3 HAOS source profile after matching
  official System Monitor/state source semantics; live freshness remains unqualified.
- Reuse the enabled heartbeat profile's approved StateAPI without new credentials
  or permissions. Host bindings without that bootstrap path fail closed.
- Preserve heartbeat checks, metrics bearer/token continuity and loopback/NetBird
  listener policy.
- Publish the qualified private image and promote its authenticated metadata.
  Original amd64/arm64 image evidence covers metrics, heartbeat and optional host
  collection; ARM64 smoke used QEMU. Real host rollout and freshness acceptance
  remain pending.

## 0.2.0 — qualified private image and catalog metadata

- Wire requested image smoke profiles through both platform builds, original build
  evidence and private metadata qualification. Runtime heartbeat remains disabled
  by default; original metrics-only artifacts retain their legacy qualification.
- Require two completed source/version/config-bound platform reports before
  retaining original profile coverage. The private image and catalog metadata
  were published and the native pilot was updated separately.

- Gate requested heartbeat profile coverage in the existing release and qualification
  APIs and CLIs, preserving legacy metrics-only original artifacts and provenance.
- Document the existing opt-in runtime, private profile/handoff custody and the
  qualified enabled image coverage and remaining full native and live acceptance gates.
- Add offline profile parity and deterministic shared shutdown-budget/no-replay
  regression coverage. Full heartbeat/provider/outage qualification remains
  separate from the native image update.

## 0.1.2 — pilot release qualification

- Wait for service readiness before asserting process identity after restart.
  A stable token can already exist while one-time root bootstrap is in progress.

## 0.1.1 — unpublished CI qualification

- Correct the isolated CI container capability set for one-time private state
  initialization. The service still drops all effective capabilities before
  serving; application permissions and runtime behavior are unchanged.
- Keep the unsuccessful, unpublished 0.1.0 source tag immutable.

## 0.1.0 — pilot

- Compose the existing Core/Supervisor/data-volume collectors and scheduler.
- Fixed GET-only Supervisor origin; authenticated metrics on a selected loopback
  or CGNAT overlay address. Manual startup, bounded HTTP workers, no Docker API.
- Stable private metrics token and hard privilege drop before serving requests.
