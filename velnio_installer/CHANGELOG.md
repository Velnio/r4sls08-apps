# Changelog

## 1.0.22 — Velnio 0.7.4

- Preserve shared Home Assistant component setup when telemetry startup is cancelled or rolled back, allowing a subsequent entry reload to recover.
- Include controlled regression coverage for setup cancellation and event acknowledgement ordering.
- Keep the private GHCR image, Supervisor Registry credentials, transactional backups, rollback and repeated no-op startup.

## 1.0.21 — Velnio 0.7.3

- Pull a private prebuilt GHCR image using Supervisor Registry credentials.
- Remove the separate github_token option and GitHub API downloader.
- Ignore retained legacy token options without forwarding or logging them.
- Preserve the verified 0.7.3 payload, transaction recovery, rollback and no-op behavior.
- Keep native source, ZIPs and container payloads private.

## 1.0.20

- Remove the bundled integration and require the user's own GitHub PAT to download the pinned release from the private Velnio repository.
- Build the public Installer on the HA device; no public container layers contain the integration.
- Verify package and manifest checksums before touching the installed integration.
- Preserve transactional backups, rollback, content no-op behavior and existing P8 settings.
- Withdraw public integration ZIPs and source archives from earlier releases and make their container images private.

## 1.0.19 — Velnio 0.7.3

- Include offline Velnio brand icons and wordmarks in both themes and densities.
- Deliver the current native P8 integration, readable names and RS485 address settings.
- Preserve LED feedback after direct LED control and restore target states after a P8 reconnects.
- Retain entity IDs, button bindings, configuration and durable inventory/session authority.
- Verify deterministic packaging, both installer architectures and selected source companions.

## 1.0.18 — Velnio 0.4.1

- Earlier experimental release adding the exact P8 firmware 0.4.0 profile.
