FROM        registry.access.redhat.com/ubi8/python-39:latest

WORKDIR     /dashdotdb

COPY        . ./

RUN         pip3 install --no-cache-dir . && \
            pip3 install --no-cache-dir gunicorn

ENTRYPOINT  ["./entrypoint.sh"]
