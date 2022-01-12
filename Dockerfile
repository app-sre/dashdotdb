FROM        registry.access.redhat.com/ubi8/python-38

WORKDIR     /dashdotdb

COPY        . ./

RUN         pip3 install .
RUN         pip3 install gunicorn

ENTRYPOINT  ["./entrypoint.sh"]
