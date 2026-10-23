FROM python:3.14.6-alpine3.23@sha256:b165067c5afc37fa5608a3c05609cc3d51aafd808a30fbfd822ee594fef55ad4

ARG BUILD_VERSION=1.0.20
ARG BUILD_ARCH
WORKDIR /opt/velnio-installer
COPY runtime/__init__.py runtime/__main__.py runtime/catalog.py runtime/installer.py runtime/supervisor.py runtime/private_release.py runtime/
COPY private-release.json LICENSE NOTICE ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
LABEL io.hass.name="Velnio Installer" \
      io.hass.description="Download a private Velnio integration using your own PAT" \
      io.hass.type="addon" \
      io.hass.version="${BUILD_VERSION}" \
      io.hass.arch="${BUILD_ARCH}" \
      org.opencontainers.image.source="https://github.com/Velnio/r4sls08-apps"
ENTRYPOINT ["python", "-m", "runtime"]
