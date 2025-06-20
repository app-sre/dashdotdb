##############
# base image #
##############
FROM registry.access.redhat.com/ubi9/python-39:9.6-1749743801@sha256:7d7dbfe4e208b4c71db010f2115d66aa6ba03034abe997ba274503f5283beb39 AS base

COPY        LICENSE /licenses/LICENSE

#################
# builder image #
#################
FROM base as builder

ARG UV_SRC_IMAGE=ghcr.io/astral-sh/uv:0.7.13@sha256:6c1e19020ec221986a210027040044a5df8de762eb36d5240e382bc41d7a9043

# Get the uv binary from upstream
COPY --from=${UV_SRC_IMAGE} /uv /bin/uv

ENV \
  UV_COMPILE_BYTECODE="true" \
  UV_NO_CACHE=true \
  # inherits from base image
  UV_PROJECT_ENVIRONMENT=$APP_ROOT

COPY --chown=1001:0 \
    pyproject.toml  \
    uv.lock         \
  ./

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
  UV_NO_CACHE=true

COPY --from=builder /opt/app-root /opt/app-root
COPY --chown=1001:0 \
  /entrypoint.sh    \
./bin/

# Copy the database migrations for Flask-SQLAlchemy
COPY --chown=1001:0 \
  migrations        \
./migrations/

ENTRYPOINT [ "entrypoint.sh" ]
