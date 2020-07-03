FROM        centos:8

WORKDIR     /dashdotdb

COPY        . ./

RUN         dnf -y install python36
RUN         pip3 install .
RUN         pip3 install gunicorn

ENTRYPOINT  ["./entrypoint.sh"]
