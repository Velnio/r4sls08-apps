# Velnio Apps

Home Assistant App repository for the Velnio R4SLS08 integration installer. The App
metadata is public; its versioned installer image and integration payload remain
private in `ghcr.io/un0know/r4sls08-installer`.

## Health Agent

This shared catalog also carries the independently versioned Velnio Health Agent
pilot. Its private image is `ghcr.io/velnio/velnio-health-agent`; see
[Health Agent documentation](velnio_health/DOCS.md) after its release is published.
Installer releases preserve Health Agent metadata and do not update its image.

## Velnio

Velnio Installer **1.0.21** installs native integration **0.7.3** from the private `ghcr.io/velnio/velnio-installer` image. Home Assistant Supervisor uses your existing **Registry credentials** for `ghcr.io`; there is no `github_token` App option. This public catalog contains only generic Installer code, build metadata and documentation. Add this repository to the Home Assistant App Store and read the [installation and recovery instructions](velnio_installer/DOCS.md).

This release includes P8 button bindings, LED feedback, readable names, address settings, recovery after reconnects and local Velnio logos. Two P8/V10 boards with firmware 0.4.0 were physically qualified on HA Core 2026.9.4, including complete power loss. Capacity with fifty physical boards and arbitrary firmware/HA versions is outside that qualification. This is a 0.7.3 release and does not claim completion of the historical 1.0 qualification scope.

Earlier public integration ZIPs/source archives have been withdrawn and the bundled container images made private. Public releases contain Installer metadata and documentation; integration releases and container payloads remain private.

Support: [GitHub Issues](https://github.com/Velnio/r4sls08-apps/issues), maintained by Mijoo s.r.o. The existing R4, Health and SFTP entries are independently versioned.
