# Velnio Installer

Installer **1.0.20** downloads integration **0.7.3** from the private
`Velnio/velnio-ha` repository using **your own GitHub personal access token**.
The public Installer contains the downloader and transactional installation
runtime. It does not include the integration, a shared token or cached payloads.

## Install or update

1. Add [Velnio Apps](https://github.com/Velnio/r4sls08-apps) to the Home Assistant App Store and refresh the store.
2. Install or update **Velnio Installer 1.0.20**. Home Assistant builds this version on your device from the public Dockerfile; internet access is required.
3. In the App's Configuration tab, enter your token in **github_token**, save and start the App.
4. Wait for `VELNIO_INSTALLER_READY: installed` or `unchanged` in the log.

The token's owner must already have read access to the private repository. A PAT
does not grant repository access by itself. Prefer a fine-grained token with
resource owner **Velnio**, selected repository **velnio-ha**, and **Contents:
read-only**. Complete any organization approval required by GitHub. A classic
PAT with private repository read access also works, but has broader permissions.
You do not need `write:packages`, `delete:packages` or write access to repository contents.

The token is configured through Home Assistant's masked password option. It is
read from the Supervisor-managed App options at runtime. It is not a Docker build
argument, environment variable, command-line argument or part of the public
repository/image. Protect HA backups, which can contain App options.

Missing, expired or unauthorized tokens stop installation before changes to the
integration or a Core restart. Log messages do not include the token or GitHub
response bodies. Downloads are bounded, checked against pinned SHA-256 digests,
and verified against the immutable per-file manifest before installation. The
PAT is sent only to `api.github.com`; asset redirects do not receive it.

Starting the App installs under `/config/custom_components/velnio`. It may restart
Home Assistant Core after a successful configuration check. Starting it again
with the same installed files is a no-op and does not restart Core. A newer
installed integration is preserved. A new integration release requires a new
Installer release with updated pins; it never silently downloads a moving branch.

## Recovery and existing settings

Verified backups, transaction journals, inventory/session authority, config entry
IDs, bindings and LED feedback keep their existing locations. The App does not
flash P8 firmware or create another serial-port owner. Existing installations
continue operating after old public release assets and images are withdrawn.

`backup_count`, `health_timeout`, `retry_failed_release`, and `rollback_to` retain
their previous meanings. Use a known backup ID for an explicit rollback. Verified
local rollback, pending transaction recovery and acknowledgement of an interrupted
rollback remain available without a working PAT or GitHub connection. A start
that finds an unfinished transaction performs recovery only; start it again to
download and install once recovery is complete. Do not delete recovery state after an
ambiguous Core restart; inspect the App log first.

Versions 1.0.15, 1.0.17, 1.0.18 and 1.0.19 bundled the integration. Their public
integration ZIPs/source archives have been withdrawn and their container package
is private. Version 1.0.20 is a breaking configuration update because a token is
now required for installation and updates.

SFTP, R4 and Health Apps remain independently versioned. Their credentials and
configuration are separate. Support: [Velnio Apps issues](https://github.com/Velnio/r4sls08-apps/issues).
