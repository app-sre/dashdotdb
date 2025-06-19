##############
# base image #
##############
FROM registry.access.redhat.com/ubi9/python-39:9.5-1739799514@sha256:9bbc4cfeac896544ab3eafa088c3d6995e82592362d374606f00d221f2986fe0 as base

COPY        LICENSE /licenses/LICENSE

#################
# builder image #
#################
FROM base as builder

# Get the uv binary from upstream
COPY --from=ghcr.io/astral-sh/uv:0.6.11@sha256:fb91e82e8643382d5bce074ba0d167677d678faff4bd518dac670476d19b159c /uv /bin/uv

ENV \
  UV_COMPILE_BYTECODE="true" \
  UV_NO_CACHE=true \
  # inherits from base image
  UV_PROJECT_ENVIRONMENT=$APP_ROOT

COPY --chown=1001:0 \
    pyproject.toml  \
    uv.lock         \
  /dashdotdb/

USER        1001
WORKDIR     /dashdotdb

# Test if the lock file is up to date
RUN \
  uv lock \
    --check

# Install project dependencies for runtime
RUN \
  uv sync \
    --no-group=dev \
    --frozen       \
    --no-install-project \
    --python /usr/bin/python3

COPY --chown=1001:0 \
    dashdotdb \
  ./dashdotdb

RUN \
  uv sync \
    --frozen \
    --no-group dev \
    --python /usr/bin/python3

##############
# test image #
##############
FROM builder as test

ENV \
  UV_COMPILE_BYTECODE="true" \
  UV_NO_CACHE=true \
  # inherits from base image
  UV_PROJECT_ENVIRONMENT=$APP_ROOT

COPY \
    Makefile \
    .pylintrc \
  ./
# Install dev group deps for the test
RUN \
  uv sync     \
  --group dev \
  --frozen

# Skip container engine checks and don't bother to run the checks in an
# --isolated environment because the test container is logically isolated
# already.
RUN \
  make \
    CONTAINER_ENGINE=skip \
    UV_USE_ISOLATED=no \
    check

##############
# Prod image #
##############
FROM base AS prod

ENV \
  UV_COMPILE_BYTECODE="true" \
  UV_NO_CACHE=true \
  # inherits from base image
  UV_PROJECT_ENVIRONMENT=$APP_ROOT

COPY --from=builder /opt/app-root /opt/app-root
ENTRYPOINT [ "entrypoint.sh" ]
