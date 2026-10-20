# Velnio Apps

Home Assistant App repository for the Velnio R4SLS08 integration installer. The App
metadata is public; its versioned installer image and integration payload remain
private in `ghcr.io/un0know/r4sls08-installer`.

## Health Agent

This shared catalog also carries the independently versioned Velnio Health Agent
pilot. Its private image is `ghcr.io/velnio/velnio-health-agent`; see
[Health Agent documentation](velnio_health/DOCS.md) after its release is published.
Installer releases preserve Health Agent metadata and do not update its image.

## Velnio — experimental

Velnio Installer App **1.0.15** installs integration **0.2.2** from a separate public image on ARM64 and AMD64. Add this repository to the Home Assistant App Store and read [installation and recovery instructions](velnio_installer/DOCS.md).

This is an experimental evaluation release: physical P8/V10 timing, capacity and soak qualification remain open. Optional temperature and complete health entities remain unfinished. It is not stable 1.0. See [release notes, exact sources and licenses](https://github.com/Velnio/r4sls08-apps/releases/tag/velnio-0.2.2-app-1.0.15-experimental.1).

Support: [GitHub Issues](https://github.com/Velnio/r4sls08-apps/issues), owned by Mijoo s.r.o.; first feedback evaluation 14 calendar days after publication, with no promised response SLA. The existing R4, Health and SFTP catalog entries are independent.
