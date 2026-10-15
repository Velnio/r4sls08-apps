# Changelog

## 0.2.0 — private image release

- Wire requested image smoke profiles through both platform builds, original build
  evidence and private metadata qualification. Runtime heartbeat remains disabled
  by default; original metrics-only artifacts retain their legacy qualification.
- Require two completed source/version/config-bound platform reports before
  retaining original profile coverage. Original metrics-only and enabled image
  smokes passed on amd64 and arm64; native HA and live acceptance remain pending.

- Gate requested heartbeat profile coverage in the existing release and qualification
  APIs and CLIs, preserving legacy metrics-only original artifacts and provenance.
- Document the existing opt-in runtime, private profile/handoff custody and the
  qualified enabled image coverage and remaining native HA and live acceptance gates.
- Add offline profile parity and deterministic shared shutdown-budget/no-replay
  regression coverage. Native HA and live qualification remain pending.

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
