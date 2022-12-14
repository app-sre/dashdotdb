FROM registry.access.redhat.com/ubi8/python-39:latest AS builder

ARG psycopg2_version=2.9.5

USER 0

RUN set -eux && \
  mkdir -p /build && \
  chown 1001 /build

WORKDIR /build

RUN set -eux && \
  dnf upgrade -y && \
  dnf install -y libpq-devel && \
  dnf install -y python3-devel

USER 1001

RUN set -eux && \
  git clone https://github.com/psycopg/psycopg2 . && \
  git switch -c ${psycopg2_version//\./_}

RUN set -eux && \
  python setup.py bdist_egg && \
  mv -f ./dist/*.egg .

FROM registry.access.redhat.com/ubi8/python-39:latest

COPY --from=builder /build/psycopg2-*.egg ./

USER 0

ENV PIP_DISABLE_PIP_VERSION_CHECK 1

RUN set -eux && \
  python3 -m easy_install psycopg2-*.egg && \
  rm -f psycopg2-*.egg && \
  pip3 list

WORKDIR /dashdotdb

COPY . ./

ENV PIP_NO_CACHE_DIR 1

RUN set -eux && \
  pip3 install gunicorn && \
  pip3 install . && \
  pip3 list

USER 1001

ENTRYPOINT ["./entrypoint.sh"]
