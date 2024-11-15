FROM        registry.access.redhat.com/ubi9/python-39:1-197.1726696853@sha256:12644d1a2d214bd1be7eac3a9b1e983a987d9452b78e4c6be9c863d5038b9338 as prod

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

FROM        registry.access.redhat.com/ubi9/python-39:1-197.1726696853@sha256:12644d1a2d214bd1be7eac3a9b1e983a987d9452b78e4c6be9c863d5038b9338 as test

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

