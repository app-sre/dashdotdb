FROM        registry.access.redhat.com/ubi9/python-39:9.5-1743508348@sha256:dd4267b8fae4fbaeefbc5396057cf4acfcc6e4147a5e1c1eb54240e2d6c1b1e6 as prod

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

FROM        registry.access.redhat.com/ubi9/python-39:9.5-1743508348@sha256:dd4267b8fae4fbaeefbc5396057cf4acfcc6e4147a5e1c1eb54240e2d6c1b1e6 as test

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

