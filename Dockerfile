FROM        registry.access.redhat.com/ubi8/python-39:1-201.1729679484

COPY        . ./

RUN         pip3 install --no-cache-dir . && \
            pip3 install --no-cache-dir gunicorn

ENTRYPOINT  ["./entrypoint.sh"]
