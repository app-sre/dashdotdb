##############
# base image #
##############
FROM registry.access.redhat.com/ubi9/python-314@sha256:194df4e35e0e5467e1b57266f4d61f821e1b1f567135f074d23066d3604ae653 AS base

ENV FLASK_APP=dashdotdb

COPY        LICENSE /licenses/LICENSE

#################
# builder image #
#################
FROM base AS builder

# Get the uv binary from upstream
COPY --from=ghcr.io/astral-sh/uv:0.11.13@sha256:841c8e6fe30a8b07b4478d12d0c608cba6de66102d29d65d1cc423af86051563 /uv /bin/uv

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
    --python $(which python3)

COPY --chown=1001:0 \
    dashdotdb \
  ./dashdotdb

RUN \
  uv sync \
    --frozen \
    --no-group dev \
    --python $(which python3)

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
