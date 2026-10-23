# Velnio public App catalog

This repository may publish the generic Installer runtime, build recipe, metadata,
logos and documentation. Native integration code, integration ZIPs, source-material
archives, shared tokens, and container layers containing the integration stay private.

Supervisor pulls the PRIVATE ghcr.io/velnio/velnio-installer image using the user's
Home Assistant Registry credentials. The App receives no registry PAT and has no
GitHub token option. Never expose Docker API access, credentials in build arguments,
image layers, logs or this repository. Do not make withdrawn payloads public again.

Public CI tests the generic runtime and catalog only. Build contexts with native
payloads must stay private. Qualify both architectures against the exact private
release file map, install/no-op, backup and rollback tests before publishing a new
immutable image tag. Verify package visibility and anonymous denial before and after.

Before GitHub writes verify Un0kNow, target repository and Git authentication.
Preserve independently versioned R4, Health and SFTP entries.
