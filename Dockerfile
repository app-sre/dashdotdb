FROM        registry.access.redhat.com/ubi8/python-39

WORKDIR     /dashdotdb

COPY        . ./

USER        root

RUN         pip3 install --no-cache-dir . && \
            pip3 install --no-cache-dir gunicorn

USER        default

ENTRYPOINT  ["./entrypoint.sh"]
