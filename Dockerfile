FROM        registry.access.redhat.com/ubi9/python-39:9.6-1749743801@sha256:7d7dbfe4e208b4c71db010f2115d66aa6ba03034abe997ba274503f5283beb39 as prod

COPY --from=ghcr.io/astral-sh/uv:0.7.13@sha256:6c1e19020ec221986a210027040044a5df8de762eb36d5240e382bc41d7a9043 /uv /bin/uv

COPY --chown=1001:0 pyproject.toml uv.lock README.md /dashdotdb/
COPY        LICENSE /licenses/LICENSE
USER        1001
WORKDIR     /dashdotdb

ENV \
  UV_COMPILE_BYTECODE="true" \
  UV_NO_CACHE=true
RUN \
  uv \
    sync \
      --no-group=dev \
      --frozen       \
      --python /usr/bin/python3

COPY        --chown=1001:0 . ./


ENTRYPOINT  ["./entrypoint.sh"]

FROM        registry.access.redhat.com/ubi9/python-39:9.6-1749743801@sha256:7d7dbfe4e208b4c71db010f2115d66aa6ba03034abe997ba274503f5283beb39 as test
COPY --from=prod /bin/uv /bin/uv

USER        root
COPY        LICENSE /licenses/LICENSE
WORKDIR     /dashdotdb
RUN         chown -R 1001:0 /dashdotdb
USER        1001
COPY        --from=prod /dashdotdb ./

# we run inside a container, so there won't be a container engine (eg podman or
# docker) available, so skip that check. Additionally, use a single environment
# (eg, not --isolated) for `make check`; we're in a container, that's pretty
# good isolation already.
RUN \
  make \
    CONTAINER_ENGINE=skip \
    UV_USE_ISOLATED=no \
    check

ENTRYPOINT  ["./entrypoint.sh"]

