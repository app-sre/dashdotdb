FROM        registry.access.redhat.com/ubi9/python-39:1-1734610342@sha256:dde5068ba8fd81eef41a9128ddad2b99e2e02e5869ffe925c605b609a0ad7bbb as prod

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

FROM        registry.access.redhat.com/ubi9/python-39:1-1734610342@sha256:dde5068ba8fd81eef41a9128ddad2b99e2e02e5869ffe925c605b609a0ad7bbb as test

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

