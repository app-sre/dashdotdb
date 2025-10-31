##############
# base image #
##############
FROM registry.access.redhat.com/ubi9/python-39:9.6-1760372481@sha256:dee7605bfc0cc89b83075937cd48ff7b61bf5e396f8bd2ae13e7f7299be53326 AS base

COPY        LICENSE /licenses/LICENSE

#################
# builder image #
#################
FROM base AS builder

# Get the uv binary from upstream
COPY --from=ghcr.io/astral-sh/uv:0.9.7@sha256:ba4857bf2a068e9bc0e64eed8563b065908a4cd6bfb66b531a9c424c8e25e142 /uv /bin/uv

ENV \
  UV_COMPILE_BYTECODE="true" \
  UV_NO_CACHE=true \
  # inherits from base image
  UV_PROJECT_ENVIRONMENT=$APP_ROOT

COPY --chown=1001:0 \
    pyproject.toml  \
    uv.lock         \
  ./

# Copy the database migrations for Flask-SQLAlchemy
COPY --chown=1001:0 \
  migrations        \
./migrations/

USER        1001

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
FROM builder AS test

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

COPY --from=builder \
    /opt/app-root     \
  /opt/app-root
COPY --chown=1001:0 \
    entrypoint.sh    \
  ./

ENTRYPOINT [ "/opt/app-root/src/entrypoint.sh" ]
