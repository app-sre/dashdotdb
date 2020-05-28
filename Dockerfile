FROM        centos/python-36-centos7

WORKDIR     /dashdotdb

COPY        . ./

RUN         pip install .
RUN         pip install gunicorn

ENTRYPOINT  ["gunicorn", "dashdotdb:app"]
CMD         ["--workers", "1", "--threads",  "8", "--bind", "0.0.0.0:8080"]
