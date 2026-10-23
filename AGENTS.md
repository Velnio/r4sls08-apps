# Velnio public App catalog

This repository may publish the generic Installer, metadata, logos and documentation.
Velnio integration code, integration ZIPs, source-material archives, shared tokens,
and container layers containing the integration must remain private.

The Installer fetches immutable release assets from `Velnio/velnio-ha` using the
user's own PAT at runtime. Never add credentials to build arguments, images, logs
or this repository. Do not restore the withdrawn public payload releases/images.

Verify the public Installer with `python -m unittest discover -s tests -v` and
build/test both supported architectures. Preserve the transactional install,
backup, rollback and no-op behavior. Public release assets must be reviewed
against this boundary before upload; GitHub account/remote checks still apply.
