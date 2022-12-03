FROM        registry.access.redhat.com/ubi8/python-39

WORKDIR     /dashdotdb

COPY        . ./

RUN         yum install python3-dev libpq-dev
RUN         pip3 install --no-cache-dir . && \
            pip3 install --no-cache-dir gunicorn

ENTRYPOINT  ["./entrypoint.sh"]
