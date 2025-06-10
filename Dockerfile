FROM        registry.access.redhat.com/ubi9/python-39:9.5-1739799514@sha256:9bbc4cfeac896544ab3eafa088c3d6995e82592362d374606f00d221f2986fe0 as prod

COPY --from=ghcr.io/astral-sh/uv:0.6.11@sha256:fb91e82e8643382d5bce074ba0d167677d678faff4bd518dac670476d19b159c /uv /bin/uv

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

FROM        registry.access.redhat.com/ubi9/python-39:9.5-1739799514@sha256:9bbc4cfeac896544ab3eafa088c3d6995e82592362d374606f00d221f2986fe0 as test
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

