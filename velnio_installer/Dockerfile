FROM python:3.14.6-alpine3.23@sha256:b165067c5afc37fa5608a3c05609cc3d51aafd808a30fbfd822ee594fef55ad4 AS pruned
COPY prune_runtime.py /tmp/prune_runtime.py
RUN python -B /tmp/prune_runtime.py && rm /tmp/prune_runtime.py

# Copy the pruned filesystem into a new root: removed bytes are absent from all final layers.
FROM scratch
COPY --from=pruned / /
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    PYTHON_VERSION=3.14.6 \
    PYTHON_SHA256=143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63

ARG BUILD_VERSION=1.0.21
ARG BUILD_ARCH
WORKDIR /opt/r4sls08
COPY runtime/ runtime/
COPY payload/ payload/
COPY release-velnio.json ./
COPY LICENSE NOTICE ./
COPY legal/ /opt/velnio/legal/
RUN python -c 'import json; value=json.load(open("release-velnio.json")); assert value["app_version"] == "'"${BUILD_VERSION}"'"' \
    && chmod -R a-w /opt/r4sls08 /opt/velnio/legal \
    && find /opt/r4sls08 /opt/velnio/legal -type d -exec chmod 0555 {} + \
    && find /opt/r4sls08 /opt/velnio/legal -type f -exec chmod 0444 {} +

LABEL io.hass.name="Velnio Installer" \
      io.hass.description="Transactional installer for Velnio integrations" \
      io.hass.type="app" \
      io.hass.version="${BUILD_VERSION}" \
      io.hass.arch="${BUILD_ARCH}" \
      org.opencontainers.image.title="Velnio Installer" \
      org.opencontainers.image.version="${BUILD_VERSION}" \
      org.opencontainers.image.source="https://github.com/Velnio/r4sls08-apps"

ENTRYPOINT ["python", "-m", "runtime"]
