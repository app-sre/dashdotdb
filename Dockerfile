FROM        registry.access.redhat.com/ubi9/python-39:1-197.1726696853

COPY        . ./

RUN         pip3 install --no-cache-dir . && \
            pip3 install --no-cache-dir gunicorn

ENTRYPOINT  ["./entrypoint.sh"]
