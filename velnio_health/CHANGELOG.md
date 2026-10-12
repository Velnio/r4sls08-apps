# Changelog

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
