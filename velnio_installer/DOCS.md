# Velnio Installer

Installer **1.0.23** installs integration **0.7.4** bundled in the PRIVATE
`ghcr.io/velnio/velnio-installer` image, for ARM64 and AMD64. This public repository
contains the generic Installer runtime, recipe and App metadata. Native integration
code and payload archives are not published here.

## Install or update

1. In Home Assistant, open **Settings → Apps → App Store → ⋮ → Registries** (Registry credentials), or `/config/apps/registries` on your HA instance.
2. Add or keep the `ghcr.io` entry: your GitHub username and your own PAT **classic** with **read:packages** in the **Password** field. Its owner must already have Read access to the private Velnio Installer package. Complete GitHub organization SSO authorization when required.
3. Add [Velnio Apps](https://github.com/Velnio/r4sls08-apps) to the App Store and refresh it.
4. Install or update **Velnio Installer 1.0.23**, then start it. Wait for `VELNIO_INSTALLER_READY: installed` or `unchanged` in its log.

There is **no github_token field** in App Configuration. Do not copy Registry
credentials into App options. Supervisor authenticates the image pull; the running
Installer does not receive the registry PAT. Do not grant `write:packages`,
`delete:packages` or source repository access just to install this image. GitHub
currently requires a classic PAT for GHCR; package access is also limited by the
account's package permissions. Prefer an account with access only to needed packages.
Protect Supervisor data and HA backups, which may contain credentials.

Official references: [Home Assistant registry credentials](https://contributors.home-assistant.io/apps/supervisor-api/host/#post-dockerregistries),
[GitHub Container Registry authentication](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry).

If the pull is denied, check expiry, account package access, organization approval
and the `ghcr.io` registry entry. The integration is not changed by a failed pull.
Once pulled, installation, no-op and local recovery use the verified bundled payload
without contacting GitHub. Published version tags must never be overwritten; each
release records its index and platform digests.

Starting the App installs under `/config/custom_components/velnio` and may restart
Home Assistant Core after a successful configuration check. Starting again with the
same files does not restart Core. A newer installed integration is preserved.
The Installer never downloads a moving source branch or flashes P8 firmware.

## Recovery and existing settings

Existing transaction journals, backups, inventory/session authority, config entry
IDs, entities, bindings and LED feedback remain in their existing locations. The
App does not create another serial-port owner. `backup_count`, `health_timeout`,
`retry_failed_release` and `rollback_to` retain their previous meanings. Use a known
backup ID for explicit rollback. Local rollback, pending transaction recovery and
acknowledgement of an interrupted rollback use verified local state. A start with
an unfinished transaction performs recovery only; inspect the log before starting
again. Do not delete recovery state after an ambiguous Core restart.

Version 1.0.20 used a separate GitHub API token and a local build. Version 1.0.21
replaces it with a private prebuilt image and Supervisor Registry credentials.
An obsolete `github_token` value retained by Supervisor is ignored, never used or
logged; remove that obsolete key from saved options when upgrading. It is absent
from the new configuration schema. Never remove or alter unrelated options.

Public integration ZIPs and source archives from older releases remain withdrawn;
their container images remain private. Authorized recipients of a private image can
inspect the code it installs. Private distribution controls access to the package.

R4, Health and SFTP Apps remain independently versioned. Support:
[Velnio Apps issues](https://github.com/Velnio/r4sls08-apps/issues).
