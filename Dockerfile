FROM        centos:8

WORKDIR     /dashdotdb

COPY        . ./

RUN         dnf -y install python36
RUN         pip3 install .
RUN         pip3 install gunicorn

ENTRYPOINT  ["gunicorn", "dashdotdb:app"]
CMD         ["--workers", "1", "--threads",  "8", "--bind", "0.0.0.0:8080"]
