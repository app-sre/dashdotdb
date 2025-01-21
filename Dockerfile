FROM        registry.access.redhat.com/ubi9/python-39:9.5-1737460369@sha256:9a31f03f8b27d9065c3488bbd3650c67271c3b868eacf816ddea07ababd9fbc0 as prod

COPY        LICENSE /licenses/LICENSE
USER        1001
WORKDIR     /dashdotdb
RUN         python3 -m venv venv
ENV         VIRTUAL_ENV=/dashdotdb/venv
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"

COPY        --chown=1001:0 . ./

RUN         pip3 install --no-cache-dir . && \
            pip3 install --no-cache-dir gunicorn

ENTRYPOINT  ["./entrypoint.sh"]

FROM        registry.access.redhat.com/ubi9/python-39:9.5-1737460369@sha256:9a31f03f8b27d9065c3488bbd3650c67271c3b868eacf816ddea07ababd9fbc0 as test

USER        root
COPY        LICENSE /licenses/LICENSE
WORKDIR     /dashdotdb
RUN         chown -R 1001:0 /dashdotdb
USER        1001
ENV         VIRTUAL_ENV=/dashdotdb/venv
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
COPY        --from=prod /dashdotdb ./

RUN         pip3 install --no-cache-dir -r requirements-check.txt
RUN         flake8 dashdotdb && \
            mypy --install-types --non-interactive && \
            pylint dashdotdb

ENTRYPOINT  ["./entrypoint.sh"]

