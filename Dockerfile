FROM        registry.access.redhat.com/ubi8/python-36

WORKDIR     /dashdotdb

COPY        . ./

RUN         pip3 install .
RUN         pip3 install gunicorn

ENTRYPOINT  ["./entrypoint.sh"]
