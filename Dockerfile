##############
# base image #
##############
FROM registry.access.redhat.com/ubi9/python-314@sha256:0390aa32a22acd8da70b09dda3049572d99ff1b1329abcce46fe1fa8093c45ee AS base

ENV FLASK_APP=dashdotdb

COPY        LICENSE /licenses/LICENSE

#################
# builder image #
#################
FROM base AS builder

# Get the uv binary from upstream
COPY --from=ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 /uv /bin/uv

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
